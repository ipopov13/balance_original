# TODO: Have the command dicts in the windows/contents be:
# {commandObject: method}
# and use the keys when the help is needed.

class Command:
    character = '(na)'
    hint = '(na)'
    description = '(na)'

    def __eq__(self, other):
        return self.character == other

    def __hash__(self):
        return hash(self.character)


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


class LoadGame(Command):
    character = 'l'
    hint = '(l)oad'
    description = 'Load a saved game'


if __name__ == '__main__':
    back = Back()
    command_dict = {back: 'back'}
    assert back == 'b'
    assert command_dict.get(back) == 'back'
    assert command_dict.get('b') == 'back'
    dict1 = {GetHelp(): '1', NewGame():'3'}
    dict2 = {GetHelp(): '2'}
    assert len(set(dict1) & set(dict2)) == 1
