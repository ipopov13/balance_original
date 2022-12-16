from abc import ABC, abstractmethod
from content_types import CommandsList


class Window(ABC):
    _default_size = (25, 80)
    _default_top_left = (0, 0)

    def __init__(self, size=_default_size, top_left=_default_top_left, ui=None, contents=()):
        if ui is None:
            raise ValueError(f"Window {self.__class__} must be initialized with a UI!")
        self.ui = ui
        self.size = size
        self.top_left = top_left
        self._contents = contents

    @abstractmethod
    def _commands(self) -> dict:
        """The mapping of commands&methods specific for the window"""
        raise NotImplementedError(f'Window {self.__class__} must define a _commands() method!')

    @abstractmethod
    def _organize_content_data(self) -> str:
        """Windows use this method to collect and organize their content"""
        raise NotImplementedError(f'Window {self.__class__} must define a _collect_content_data() method!')

    def _content_commands(self) -> dict:
        """The mapping of commands&methods specific for the window content"""
        content_commands = {}
        for content in self._contents:
            content_commands.update(content.commands())
        return content_commands

    def get_display_data(self) -> dict:
        """Pad the content to size and position and return it to the UI"""
        content_data = self._organize_content_data()
        content_data = content_data.split('\n')
        for row_index in range(len(content_data)):
            content_data[row_index] += ' ' * (self.size[1] - len(content_data[row_index]))
        content_data += [' ' * self.size[1]] * (self.size[0] - len(content_data))
        content_data[-1] = '(?)' + content_data[-1][3:]
        content_dict = {(row_index + self.top_left[0], 0 + self.top_left[1]): row
                        for row_index, row in enumerate(content_data)}
        return content_dict

    def _available_commands(self) -> dict:
        return {**self._commands(), **self._content_commands(), **{'?': self._help_command}}

    def _empty_command(self, _) -> bool:
        return self.ui.display({(0, 0): ''})

    def _help_command(self, _) -> bool:
        help_window = OverlayWindow(size=(15, 50), top_left=(5, 20), ui=self.ui,
                                    contents=[CommandsList(self._available_commands())])
        return self.ui.add_window(help_window)

    def handle_input(self, player_input) -> bool:
        """
        Process the player command by getting the data and calling one of the UI
        methods
        """
        chosen_command = self._available_commands().get(player_input, self._empty_command)
        return chosen_command(player_input)


class WelcomeWindow(Window):

    def _set_contents(self, contents):
        pass

    def _commands(self):
        return {'n': self._new_game, 'l': self._load_game}

    def _new_game(self, _):
        return self.ui.display({(0, 0): 'new game '})

    def _load_game(self, _):
        return self.ui.display({(0, 0): 'load game'})

    def _empty_command(self, _):
        return False

    def _organize_content_data(self):
        return r'''
               ___      _   _         _   _    _   ___   ____
              |   \    / |  |        / |  |\   |  /   \ |
              |___/   /  |  |       /  |  | \  |  |     |___
              |   \  /---|  |      /---|  |  \ |  |     |
              |___/ /    |  |___| /    |  |   \|  \___/ |____

                                    ver 0.6

                                   (n)ew game
                             (l)oad a previous game'''


class OverlayWindow(Window):
    def _commands(self) -> dict:
        return {'b': self._back_command}

    def _organize_content_data(self):
        return self._contents[0].data()

    def _back_command(self, _):
        return self.ui.drop_window(self)


if __name__ == '__main__':
    window = WelcomeWindow(ui=1)
    test_content = window.get_display_data()
    for v in test_content.values():
        assert len(v) == window.size[1], str(v)
    assert len(test_content) == window.size[0]
