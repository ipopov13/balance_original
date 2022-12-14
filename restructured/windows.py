from abc import ABC, abstractmethod


class Window(ABC):
    _size = (25, 80)
    _top_left = (0, 0)

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
        #TODO: Pad the content data to the screen size
        #TODO: Adjust the coordinates of the display data to the UI coordinate
        # system using the _top_left coordinates

    def _available_commands(self) -> dict:
        return {**self._commands(), **self._content_commands()}

    @staticmethod
    def _empty_command(_):
        return {(0, 0): ''}

    def _help_command(self):
        return {(0, 0): 'help command'}

    def handle_input(self, player_input) -> dict:
        chosen_command = self._available_commands().get(player_input, self._empty_command)
        updates = chosen_command(player_input)
        return updates


class WelcomeWindow(Window):
    _data = r'''
               ___      _   _         _   _    _   ___   ____
              |   \    / |  |        / |  |\   |  /   \ |
              |___/   /  |  |       /  |  | \  |  |     |___
              |   \  /---|  |      /---|  |  \ |  |     |
              |___/ /    |  |___| /    |  |   \|  \___/ |____

                                    ver 0.6

                                   (n)ew game
                             (l)oad a previous game
                            '''

    def _format_display_data(self):
        return self._data.split('\n')

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
