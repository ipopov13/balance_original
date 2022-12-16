from abc import ABC, abstractmethod


class WindowContent(ABC):
    def __init__(self, game_object):
        self.game_object = game_object

    @abstractmethod
    def commands(self) -> dict:
        return {}

    @abstractmethod
    def data(self) -> str:
        return ''


class CommandsList(WindowContent):
    def commands(self) -> dict:
        return {}

    def data(self):
        command_descriptions = [f'{k}: {str(v)}' for k, v in self.game_object.items()]
        return '\n'.join(command_descriptions)
