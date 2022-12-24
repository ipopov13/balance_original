from abc import ABC, abstractmethod
from commands import Command
from game_objects import GameObject


class WindowContent(ABC):
    def __init__(self, game_object):
        if not self._confirm_object_type(game_object):
            raise ValueError(f'Wrong object of type {type(game_object)} passed to {self.__class__}')
        self.game_object = game_object

    @abstractmethod
    def _confirm_object_type(self, game_object):
        raise NotImplementedError(f'Class {self.__class__} must implement _confirm_object_type!')

    @staticmethod
    def commands() -> dict:
        return {}

    def data(self) -> str:
        return '(empty content)'


class SelectionList(WindowContent):
    def _confirm_object_type(self, game_object):
        assert isinstance(game_object, list)
        for obj in game_object:
            assert isinstance(obj, GameObject)
        return True

    def data(self):
        # TODO: Implement item sorting in the list
        # TODO: Implement pagination and description justifying and line splitting
        # TODO: Implement item selection characters/numbers and command handling
        item_descriptions = [f'{item.name}: {item.description}'[:65] for item in self.game_object]
        return '\n'.join(item_descriptions)


class CommandsList(WindowContent):
    def _confirm_object_type(self, game_object):
        assert isinstance(game_object, dict)
        for command in game_object:
            assert isinstance(command, Command)
        return True

    def data(self):
        command_descriptions = [f'{k.character}: {k.description}' for k in self.game_object]
        return '\n'.join(command_descriptions)
