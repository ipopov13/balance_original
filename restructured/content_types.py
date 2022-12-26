import commands


class WindowContent:
    def __init__(self, game_object):
        self.game_object = game_object

    @staticmethod
    def _own_commands():
        return {}

    def commands(self) -> dict:
        """Combine the content-specific and object-specific commands"""
        return {**self._object_commands(),
                **self._own_commands()}

    def data(self) -> str:
        return self.game_object.data()

    def _object_commands(self) -> dict:
        """The mapping of commands&methods specific for the underlying object(s)"""
        try:
            object_commands = self.game_object.commands()
        except AttributeError:
            object_commands = {}
            for obj in self.game_object:
                object_commands.update(obj.commands())
        return object_commands


class SelectionList(WindowContent):
    def __init__(self, game_object):
        super().__init__(game_object)

    def commands(self) -> dict:
        return {}

    def return_object(self, number_string):
        return self.game_object[int(number_string)]

    def data(self):
        # TODO: Implement pagination and limit page length to 10 (numbers 0-9)
        # TODO: Implement description justifying and line splitting
        sorted_list = sorted(self.game_object, key=lambda x: x.sort_key)
        item_descriptions = [f'{number}) {item.name}: {item.description}'[:65]
                             for number, item in enumerate(sorted_list)]
        return '\n'.join(item_descriptions)


class DescriptionList(WindowContent):
    """Generate a list of object descriptions from an iterable"""
    def data(self):
        command_descriptions = [f'{k.character}: {k.description}' for k in self.game_object]
        return '\n'.join(command_descriptions)


class TextInputField:
    def __init__(self):
        self._data = ''

    def commands(self) -> dict:
        return {commands.TextInput(): self._add_character,
                commands.Backspace(): self._remove_last_character}

    def _add_character(self, character):
        self._data += character

    def _remove_last_character(self):
        self._data = self._data[:-1]

    def data(self) -> str:
        return self._data
