from abc import ABC, abstractmethod
import string
from content_types import CommandsList
from game_objects import Game
import commands

# TODO: Split Window into ContentWindow (has contents) and InputWindow (has target)
class Window(ABC):
    _default_size = (25, 80)
    _default_top_left = (0, 0)

    def __init__(self, size=_default_size, top_left=_default_top_left, ui=None,
                 contents=(), border=False, title='Balance'):
        if ui is None:
            raise ValueError(f"Window {self.__class__} must be initialized with a UI!")
        self.ui = ui
        self.size = size
        self.top_left = top_left
        self._contents = contents
        self._border = border
        self._title = title

    def _commands(self) -> dict:
        """The mapping of commands&methods specific for the window"""
        return {commands.GetHelp(): self._help_command}

    @abstractmethod
    def _organize_content_data(self) -> str:
        """Windows use this method to collect and organize their content"""
        raise NotImplementedError(f'Window {self.__class__} must define a _collect_content_data() method!')

    def _content_commands(self) -> dict:
        """The mapping of commands&methods specific for the window content"""
        content_commands = {}
        for content in self._contents:
            command_dict = content.commands()
            if set(command_dict) & set(content_commands):
                raise ValueError(f'Duplicate window command "{set(command_dict) & set(content_commands)}"'
                                 f' in window {self.__class__}')
            content_commands.update(command_dict)
        return content_commands

    def get_display_data(self) -> dict:
        """Pad the content to size and position, apply borders and hints"""
        # TODO: For composite windows (i.e. game scene) this can be called by a provide_data method that sends
        #  the contents of the separate sub-windows one by one (so this method would be private). Border
        #  should be only one though, if any
        content_data = self._organize_content_data()
        content_data = content_data.split('\n')
        # Check if all content fits the line length, add ellipsis
        for row_index in range(len(content_data)):
            if len(content_data[row_index]) > self.size[-1]:
                content_data[row_index] = content_data[row_index][:self.size[-1] - 3] + '...'
        # Horizontal pad: center the longest content line
        longest_line_len = max([len(line) for line in content_data])
        left_pad = (self.size[-1] - longest_line_len) // 2
        min_right_pad = self.size[-1]
        for row_index in range(len(content_data)):
            content_data[row_index] = ' ' * left_pad + content_data[row_index]
        for row_index in range(len(content_data)):
            right_pad = (self.size[1] - len(content_data[row_index]))
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
        content_data[0] = self._title.center(self.size[-1], '-')
        content_data[-1] = '-' * self.size[-1]
        return content_data

    def _available_commands(self) -> dict:
        local_commands = self._commands()
        content_commands = self._content_commands()
        if set(local_commands) & set(content_commands):
            raise ValueError(f'Duplicate window command "{set(local_commands) & set(content_commands)}"'
                             f' in window {self.__class__}')
        return {**self._commands(), **self._content_commands()}

    def _empty_command(self, _) -> bool:
        return self.ui.display({(0, 0): ''})

    def _help_command(self, _) -> bool:
        help_window = OverlayWindow(size=(15, 50), top_left=(5, 20), ui=self.ui,
                                    contents=[CommandsList(self._available_commands())],
                                    border=True, title='Available commands')
        return self.ui.add_window(help_window)

    def handle_input(self, player_input) -> bool:
        """
        Process the player command by getting the data and calling one of the UI
        methods
        """
        chosen_command = self._available_commands().get(player_input, self._empty_command)
        return chosen_command(player_input)


class WelcomeWindow(Window):

    def _commands(self):
        return {commands.NewGame(): self._new_game,
                commands.LoadGame(): self._load_game,
                commands.GetHelp(): self._help_command}

    def _new_game(self, _):
        self.ui.game = Game()
        name_window = InputWindow(size=(3, 20), top_left=(11, 30), ui=self.ui, border=True,
                                  title='Enter your name', character_set=string.ascii_letters,
                                  target=self.ui.game.set_character_name)
        return self.ui.add_window(name_window)

    def _load_game(self, _):
        return self.ui.display({(0, 0): self.ui.game.character.name})

    def _empty_command(self, _):
        return False

    def _organize_content_data(self):
        return r''' ___      _   _         _   _    _   ___   ____
|   \    / |  |        / |  |\   |  /   \ |
|___/   /  |  |       /  |  | \  |  |     |___
|   \  /---|  |      /---|  |  \ |  |     |
|___/ /    |  |___| /    |  |   \|  \___/ |____

                    ver 0.7
                  Ivan Popov'''


class OverlayWindow(Window):
    """A closable window presenting information"""
    def _commands(self) -> dict:
        return {commands.Back(): self._back_command}

    def _organize_content_data(self):
        return self._contents[0].data()

    def _back_command(self, _):
        return self.ui.drop_window(self)


class InputWindow(Window):
    """A window for collecting multi-character user input"""

    def _organize_content_data(self) -> str:
        return ''

    def __init__(self, character_set=string.digits, target=None, **kwargs):
        super().__init__(**kwargs)
        self._character_set = character_set
        self.target = target
        self.collected_input = ''

    def _commands(self) -> dict:
        return {commands.CompleteInput(): self._complete_input}

    def _empty_command(self, char) -> bool:
        if char not in self._character_set:
            return True
        else:
            self.collected_input += char
            return self.ui.display({(self.top_left[0] + 1,
                                     self.top_left[1] + 2): self.collected_input})

    def _complete_input(self, _):
        self.target(self.collected_input)
        return self.ui.drop_window(self)


if __name__ == '__main__':
    window = WelcomeWindow(ui=1)
    test_content = window.get_display_data()
    for v in test_content.values():
        assert len(v) == window.size[1], str(v)
    assert len(test_content) == window.size[0]
