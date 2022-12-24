from abc import abstractmethod
from content_types import WindowContent
from commands import Command


class InterfaceObject:
    def __init__(self, game_object):
        if not self._confirm_object_type(game_object):
            raise ValueError(f'Wrong object of type {type(game_object)} passed to {self.__class__}')
        self.game_object = game_object

    @abstractmethod
    def _confirm_object_type(self, game_object):
        raise NotImplementedError(f'Class {self.__class__} must implement _confirm_object_type!')

    def display(self):
        content = self._content_type(self)
        return content.display()

    @property
    def display_data(self) -> str:
        return '(This is an empty object)'

    @property
    def _content_type(self):
        return WindowContent


class WelcomeScreen(InterfaceObject):
    def _confirm_object_type(self, game_object):
        return True

    def display_data(self) -> str:
        return r''' ___      _   _         _   _    _   ___   ____
|   \    / |  |        / |  |\   |  /   \ |
|___/   /  |  |       /  |  | \  |  |     |___
|   \  /---|  |      /---|  |  \ |  |     |
|___/ /    |  |___| /    |  |   \|  \___/ |____

                    ver 0.7
                  Ivan Popov'''


class CommandList(InterfaceObject):
    def _confirm_object_type(self, game_object):
        assert isinstance(game_object, dict)
        for command in game_object:
            assert isinstance(command, Command)
        return True

    def display_data(self) -> str:
        command_descriptions = [f'{k.character}: {k.description}' for k in self.game_object]
        return '\n'.join(command_descriptions)


class GameObject:
    def __init__(self):
        self.name = ''
        self.icon = '@'
        self.look_description = '(empty GameObj description)'
        self.sort_key = 0


class Character(GameObject):
    def data(self) -> str:
        if self.name == '':
            return ''
        return '(empty character data)'
