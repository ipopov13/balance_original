from abc import ABC, abstractmethod


class Window(ABC):

    @property
    def _interfaces(self):
        return {}

    def get_display_data(self):
        return self._format_display_data()

    @abstractmethod
    def _format_display_data(self):
        pass

    @property
    @abstractmethod
    def _content_interfaces(self):
        pass

    @property
    def interfaces(self) -> dict[str, int]:
        available_interfaces = self._interfaces.copy()
        available_interfaces.update(self._content_interfaces)
        return available_interfaces


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

    def _interfaces(self):
        return {'n': self._new_game, 'l': 'load game'}

    def _content_interfaces(self):
        return {}

    @staticmethod
    def _new_game(_):
        return {(0, 0): 'new game'}
