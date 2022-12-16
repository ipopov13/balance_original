# TODO: Define the commands of all windows and content here with the elements:
# command_text with hint, command character, command description, e.g.
# 'b':'(B)ack':'Return to the previous window'
# Make sure that the commands do not overlap! Register them in a dict and check!

# Have the command dicts in the windows/contents be:
# {commandObject: method}
# and use the keys when the help is needed.
# TODO: Have a {char: Command} dict to transit between the input and the object

class Command:
    def __eq__(self, other):
        return self.character == other


class BackCommand(Command):
    character = 'b'
    hint = '(B)ack'
    description = 'Return to the previous window'


if __name__ == '__main__':
    back = BackCommand()
    command_dict = {BackCommand: 'back'}
    assert back == 'b'
    assert command_dict.get(back) == 'back'
