from windows import FullScreenWindow


class WindowContent:
    def __init__(self, game_object):
        self.game_object = game_object

    @staticmethod
    def commands() -> dict:
        return {}

    def display(self):
        """Returns the Window that will display the content"""
        window = FullScreenWindow(self)
        return window

    def get_display_data(self):
        return self.game_object.display_data

    @property
    def commands(self) -> dict:
        """The mapping of commands&methods specific for the window content"""
        content_commands = {}
        for content in self._contents:
            command_dict = self._content.commands()
            if set(command_dict) & set(content_commands):
                raise ValueError(f'Duplicate window command "{set(command_dict) & set(content_commands)}"'
                                 f' in window {self.__class__}')
            content_commands.update(command_dict)
        return content_commands