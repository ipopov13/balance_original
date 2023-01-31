from abc import ABC
from time import sleep

from content_types import DescriptionList
import commands
from utils import strip_ansi_escape_sequences, horizontal_pad
import config


class Window(ABC):
    _default_size = (25, 80)
    _default_top_left = (0, 0)

    def __init__(self, size=_default_size, top_left=_default_top_left, ui=None,
                 content=None, border: bool = False, title: str = None, title_source=None):
        if ui is None:
            raise ValueError(f"Window {self.__class__} must be initialized with a UI!")
        self.ui = ui
        self.size = size
        self.top_left = top_left
        self._content = content
        self._border = border
        self._title = title
        self._title_source = title_source

    def _commands(self) -> dict:
        """The mapping of commands&methods specific for the window"""
        return {commands.GetHelp(): self._help_command}

    def get_display_data(self) -> tuple[dict, tuple[int, int]]:
        """Pad the content to size and position, apply borders and hints"""
        content_data = self._content.data().split('\n')
        content_data, left_pad, min_right_pad = horizontal_pad(content_data, self.size[-1])
        # Vertical pad: center within window size
        top_pad = (self.size[0] - len(content_data)) // 2
        bottom_pad = self.size[0] - len(content_data) - top_pad
        content_data = [' ' * self.size[1]] * top_pad + content_data
        content_data += [' ' * self.size[1]] * bottom_pad
        if self._border:
            content_data = self._apply_border(content_data,
                                              pads=[left_pad, min_right_pad, top_pad, bottom_pad])
        if bottom_pad > 0:
            content_data = self._apply_hints(content_data)
        content_dict = {(row_index + self.top_left[0], 0 + self.top_left[1]): row
                        for row_index, row in enumerate(content_data)}
        content_cursor_pos = self._content.cursor_pos()
        cursor_pos = (content_cursor_pos[0] + self.top_left[0] + top_pad,
                      content_cursor_pos[1] + self.top_left[1] + left_pad)
        return content_dict, cursor_pos

    def _apply_hints(self, content_data):
        hints = [c.hint for c in self._available_commands() if c.hint]
        hint_string = ' '.join(hints)
        if len(hint_string) > self.size[-1]:
            raise ValueError(f'Hint string too long to fit into window {self.__class__}')
        fill_character = list(set(content_data[-1]))[0]
        last_row = hint_string.center(self.size[-1], fill_character)
        content_data[-1] = last_row
        return content_data

    def _apply_border(self, content_data, pads):
        if not all([p > 0 for p in pads]):
            raise ValueError(f'Content is too big to apply border in {self.__class__},\n pads {pads}')
        title = self._title or self._title_source()
        raw_title = strip_ansi_escape_sequences(title)
        content_data[0] = raw_title.center(self.size[-1], '-').replace(raw_title, title)
        content_data[-1] = '-' * self.size[-1]
        return content_data

    def _available_commands(self) -> dict:
        local_commands = self._commands()
        content_commands = self._content.commands()
        if set(local_commands) & set(content_commands):
            raise ValueError(f'Duplicate window command "{set(local_commands) & set(content_commands)}"'
                             f' in window {self.__class__}')
        return {**local_commands, **content_commands}

    def _help_command(self, _) -> bool:
        help_window = OverlayWindow(size=(15, 50), top_left=(5, 20), ui=self.ui,
                                    content=DescriptionList(self._available_commands()),
                                    border=True, title='Available commands')
        return self.ui.add_window(help_window)

    def handle_input(self, player_input) -> bool:
        """
        Process the player command by getting the data and calling one of the UI
        methods
        """
        for command, callback in self._available_commands().items():
            if command == player_input:
                should_game_continue = callback(player_input)
                if command.changes_window:
                    self.ui.drop_window(self)
                elif self.ui.is_top(self):
                    displayed_content, cursor_pos = self.get_display_data()
                    result = self.ui.display(displayed_content, cursor_pos)
                    new_content, new_cursor_pos = self.get_display_data()
                    while new_content != displayed_content:
                        sleep(config.frame_viewing_time)
                        result = self.ui.display(new_content, new_cursor_pos)
                        displayed_content = new_content
                        new_content, new_cursor_pos = self.get_display_data()
                    return result
                return should_game_continue
        return True


class SelectionWindow(Window):

    def __init__(self, target=None, **kwargs):
        super().__init__(**kwargs)
        self.target = target

    def _commands(self) -> dict:
        return {commands.NumberSelection(self._content.max_choice): self._complete_input,
                commands.Close(): self._return_none}

    def _return_none(self, _) -> bool:
        self.target(None)
        return True

    def _complete_input(self, player_choice):
        self.target(self._content.return_object(player_choice))
        return True


class OverlayWindow(Window):
    """A closable window presenting information"""
    def _commands(self) -> dict:
        return {commands.Back(): self._back_command}

    def _back_command(self, _):
        return self.ui.drop_window(self)


class InputWindow(Window):
    """A window for collecting multi-character user input"""

    def __init__(self, target=None, **kwargs):
        super().__init__(**kwargs)
        self.target = target

    def _commands(self) -> dict:
        return {commands.CompleteInput(): self._complete_input}

    def _complete_input(self, _):
        self.target(self._content.data())
        return True

    def get_display_data(self) -> tuple[dict, tuple[int, int]]:
        content_dict, cursor_pos = super().get_display_data()
        cursor_pos = (self.top_left[0] + 1,
                      len(self._content.data()) // 2 + self.top_left[1] + self.size[1] // 2)
        return content_dict, cursor_pos


if __name__ == '__main__':
    from content_types import TextInputField

    window = Window(ui=1, content=TextInputField())
    test_content = window.get_display_data()[0]
    for v in test_content.values():
        assert len(v) == window.size[1], str(v)
    assert len(test_content) == window.size[0]
