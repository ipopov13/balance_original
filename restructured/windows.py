from abc import ABC, abstractmethod


class Window(ABC):
    _default_size = (25, 80)
    _default_top_left = (0, 0)

    def __init__(self, size=_default_size, top_left=_default_top_left, ui=None):
        if ui is None:
            raise ValueError(f"Window {self.__class__} must be initialized with a UI!")
        self.ui = ui
        self.size = size
        self.top_left = top_left

    @abstractmethod
    def _commands(self) -> dict:
        """The mapping of commands&methods specific for the window"""
        return {'?': self._help_command}

    @abstractmethod
    def _collect_content_data(self):
        raise NotImplementedError

    @abstractmethod
    def _content_commands(self) -> dict:
        """The mapping of commands&methods specific for the window content"""
        #TODO: Add automatic command collection here, drop method from children
        pass

    def get_display_data(self):
        content_data = self._collect_content_data()
        content_data = content_data.split('\n')
        for row_index in range(len(content_data)):
            content_data[row_index] += ' ' * (self.size[1] - len(content_data[row_index]))
        content_data += [' ' * self.size[1]] * (self.size[0] - len(content_data))
        content_dict = {(row_index + self.top_left[0], 0 + self.top_left[1]): row
                        for row_index, row in enumerate(content_data)}
        return content_dict

    def _available_commands(self) -> dict:
        return {**self._commands(), **self._content_commands()}

    @staticmethod
    def _empty_command(_):
        return {(0, 0): ''}

    def _help_command(self):
        return {(0, 0): 'help command'}

    def handle_input(self, player_input) -> bool:
        """
        Process the player command by getting the data and calling one of the UI
        methods
        """
        chosen_command = self._available_commands().get(player_input, self._empty_command)
        updates = chosen_command(player_input)
        return self.ui.display(updates)


class WelcomeWindow(Window):

    def _commands(self):
        return {'n': self._new_game, 'l': self._load_game}

    def _content_commands(self):
        return {}

    @staticmethod
    def _new_game(_):
        return {(0, 0): 'new game '}

    @staticmethod
    def _load_game(_):
        return {(0, 0): 'load game'}

    @staticmethod
    def _empty_command(_):
        return {}

    def _collect_content_data(self):
        return r'''
               ___      _   _         _   _    _   ___   ____
              |   \    / |  |        / |  |\   |  /   \ |
              |___/   /  |  |       /  |  | \  |  |     |___
              |   \  /---|  |      /---|  |  \ |  |     |
              |___/ /    |  |___| /    |  |   \|  \___/ |____

                                    ver 0.6

                                   (n)ew game
                             (l)oad a previous game'''


if __name__ == '__main__':
    window = WelcomeWindow(ui=1)
    content = window.get_display_data()
    for v in content.values():
        assert len(v) == window.size[1], str(v)
    assert len(content) == window.size[0]
