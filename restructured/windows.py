from abc import ABC
from content_types import DescriptionList
import commands
from utils import strip_ansi_escape_sequences


class Window(ABC):
    _default_size = (25, 80)
    _default_top_left = (0, 0)
    _should_refresh_screen = False

    def __init__(self, size=_default_size, top_left=_default_top_left, ui=None,
                 content=None, border=False, title='Balance'):
        if ui is None:
            raise ValueError(f"Window {self.__class__} must be initialized with a UI!")
        self.ui = ui
        self.size = size
        self.top_left = top_left
        self._content = content
        self._border = border
        self._title = title

    def _commands(self) -> dict:
        """The mapping of commands&methods specific for the window"""
        return {commands.GetHelp(): self._help_command}

    def get_display_data(self) -> dict:
        """Pad the content to size and position, apply borders and hints"""
        # TODO: For composite windows (i.e. game scene) this can be called by a provide_data method that sends
        #  the contents of the separate sub-windows one by one (so this method would be private). Border
        #  should be only one though, if any
        content_data = self._content.data()
        raw_content_data = strip_ansi_escape_sequences(content_data)
        raw_content_data = raw_content_data.split('\n')
        content_data = content_data.split('\n')
        # Horizontal pad: center the longest content line
        longest_line_len = max([len(line) for line in raw_content_data])
        left_pad = (self.size[-1] - longest_line_len) // 2
        min_right_pad = self.size[-1]
        for row_index in range(len(content_data)):
            content_data[row_index] = ' ' * left_pad + content_data[row_index]
        for row_index in range(len(content_data)):
            right_pad = (self.size[1] - len(raw_content_data[row_index]))
            content_data[row_index] += ' ' * right_pad
            min_right_pad = min(right_pad, min_right_pad)
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
        return content_dict

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
            raise ValueError(f'Content is too big to apply border in {self.__class__}')
        raw_title = strip_ansi_escape_sequences(self._title)
        content_data[0] = raw_title.center(self.size[-1], '-').replace(raw_title, self._title)
        content_data[-1] = '-' * self.size[-1]
        return content_data

    def _available_commands(self) -> dict:
        local_commands = self._commands()
        content_commands = self._content.commands()
        if set(local_commands) & set(content_commands):
            raise ValueError(f'Duplicate window command "{set(local_commands) & set(content_commands)}"'
                             f' in window {self.__class__}')
        return {**local_commands, **content_commands}

    def _empty_command(self, _) -> bool:
        return self.ui.display({(0, 0): ''})

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
                elif self._should_refresh_screen:
                    return self.ui.display(self.get_display_data())
                return should_game_continue
        return True


class SelectionWindow(Window):
    _should_refresh_screen = True

    def __init__(self, target=None, **kwargs):
        super().__init__(**kwargs)
        self.target = target

    def _commands(self) -> dict:
        return {commands.NumberSelection(self._content.max_choice): self._complete_input}

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
    _should_refresh_screen = True

    def __init__(self, target=None, **kwargs):
        super().__init__(**kwargs)
        self.target = target

    def _commands(self) -> dict:
        return {commands.CompleteInput(): self._complete_input}

    def _complete_input(self, _):
        self.target(self._content.data())
        return True


if __name__ == '__main__':
    from content_types import TextInputField

    window = Window(ui=1, content=TextInputField())
    test_content = window.get_display_data()
    for v in test_content.values():
        assert len(v) == window.size[1], str(v)
    assert len(test_content) == window.size[0]
