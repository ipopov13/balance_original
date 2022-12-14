from abc import ABC, abstractmethod


class Window(ABC):

    @abstractmethod
    def _commands(self) -> dict:
        """The mapping of commands&methods specific for the window"""
        return {}

    def get_display_data(self):
        return self._format_display_data()

    @abstractmethod
    def _format_display_data(self):
        pass

    @abstractmethod
    def _content_commands(self) -> dict:
        """The mapping of commands&methods specific for the window content"""
        #TODO: Add automatic command collection here, drop method from children
        pass

    @staticmethod
    def _empty_command(_):
        return {(0, 0): ''}

    def handle_input(self, player_input) -> dict:
        available_commands = {**self._commands(), **self._content_commands()}
        chosen_command = available_commands.get(player_input, self._empty_command)
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
