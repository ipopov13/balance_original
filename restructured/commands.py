import string


class Command:
    character = '(na)'
    hint = '(na)'
    description = '(na)'
    changes_window = False

    def __eq__(self, other):
        return self.character == other

    def __hash__(self):
        return hash(self.character)

    @staticmethod
    def commands():
        return {}


class TextInput(Command):
    character = string.ascii_letters + '- '
    hint = ''
    description = 'Enter text'

    def __eq__(self, other):
        return other in self.character

    def __hash__(self):
        return hash(self.character)


class CompleteInput(Command):
    character = '\r'
    hint = ''
    description = 'Send your input'


class Backspace(Command):
    character = chr(8)
    hint = ''
    description = 'Drop the last character'


class Back(Command):
    character = 'b'
    hint = '(b)ack'
    description = 'Return to the previous window'


class GetHelp(Command):
    character = '?'
    hint = '(?)Help'
    description = 'Show this screen'


class NewGame(Command):
    character = 'n'
    hint = '(n)ew game'
    description = 'Start a new game'
    changes_window = True


class LoadGame(Command):
    character = 'l'
    hint = '(l)oad'
    description = 'Load a saved game'
    changes_window = True


if __name__ == '__main__':
    back = Back()
    command_dict = {back: 'back'}
    assert back == 'b'
    assert command_dict.get(back) == 'back'
    assert command_dict.get('b') == 'back'
    dict1 = {GetHelp(): '1', NewGame():'3'}
    dict2 = {GetHelp(): '2'}
    assert len(set(dict1) & set(dict2)) == 1
