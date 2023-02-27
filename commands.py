import string
import console


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


class CharacterRangeCommand(Command):

    def __eq__(self, other):
        return other in self.character

    def __hash__(self):
        return hash(self.character)


class CharacterSheet(Command):
    character = '@'
    hint = '(@)You'
    description = 'Open the character sheet'
    changes_window = True


class LightAFire(Command):
    character = 'L'
    hint = '(L)ight a fire'
    description = 'Light a fire on the ground'


class AddToFire(Command):
    character = 'A'
    hint = '(A)dd to fire'
    description = 'Fuel the existing fire'


class Inventory(Command):
    character = 'I'
    hint = '(I)nventory'
    description = 'Open the inventory screen'
    changes_window = True


class InventoryEmpty(Command):
    character = 'q'
    hint = '(q)Empty'
    description = 'Empty the selected container'


class InventoryFill(Command):
    character = 'f'
    hint = '(f)ill'
    description = 'Fill the selected container with a suitable substance'
    changes_window = True


class InventoryPickUp(Command):
    character = 'p'
    hint = '(p)ick up'
    description = 'Put the selected item in your inventory'


class InventoryEquip(Command):
    character = 'e'
    hint = '(e)quip'
    description = 'Equip the selected item'


class InventoryEquipSlot(Command):
    character = 'e'
    hint = '(e)quip'
    description = 'Equip the selected slot'
    changes_window = True


class InventoryUnequip(Command):
    character = 'r'
    hint = '(r)emove'
    description = 'Remove the selected item'


class InventoryDrop(Command):
    character = 'd'
    hint = '(d)rop'
    description = 'Drop the selected item'


class InventoryConsume(Command):
    character = 'c'
    hint = '(c)onsume'
    description = 'Eat/drink the selected item'


class Mode(Command):
    character = 'M'
    hint = '(M)ode'
    description = 'Change mode: normal|work|stealth'


class Map(Command):
    character = 'm'
    hint = '(m)ap'
    description = 'Open the world map'
    changes_window = True


class SwitchContainers(Command):
    character = 's'
    hint = '(s)witch'
    description = 'Switch between the accessible views'


class Close(Command):
    character = 'C'
    hint = '(C)lose'
    description = 'Close the current window'
    changes_window = True


class TextInput(CharacterRangeCommand):
    character = string.ascii_letters + '- '
    hint = ''
    description = 'Enter text'


class Move(CharacterRangeCommand):
    character = '12346789'
    hint = f'(1-9){console.fg.green}Move{console.fx.end}'
    description = 'Walk in a num-pad direction'


class Sneak(CharacterRangeCommand):
    character = '12346789'
    hint = '(1-9)Sneak'
    description = 'Try to move silently'


class Work(CharacterRangeCommand):
    character = '12346789'
    hint = f'(1-9){console.fg.blue}Work{console.fx.end}'
    description = 'Work on the terrain around you'


class Look(CharacterRangeCommand):
    character = '12346789'
    hint = f'(1-9){console.fg.yellow}Look{console.fx.end}'
    description = 'Look around'


class Rest(Command):
    character = '5'
    hint = ''
    description = 'Rest and restore energy and hit points'


class Target(Command):
    character = 't'
    hint = f'({console.fg.yellow}t{console.fx.end}){console.fg.yellow}arget{console.fx.end}'
    description = 'Select your target'


class Shoot(Command):
    character = 's'
    hint = ''
    description = 'Shoot/throw at your current target'


class Stop(Command):
    character = 'S'
    hint = '(S)top'
    description = 'Stop what you are doing'


class NextPage(Command):
    character = 'n'
    hint = '(n)ext page'
    description = 'Go to the next page'


class PreviousPage(Command):
    character = 'p'
    hint = '(p)revious page'
    description = 'Go to the previous page'


class NumberSelection(CharacterRangeCommand):
    character = string.digits
    hint = ' (0-9) Choose an option '
    description = 'Enter a number'
    changes_window = True

    def __init__(self, choice_cap):
        self.character = ''.join([str(x) for x in range(choice_cap)])
        self.hint = f' (0-{choice_cap-1}) Choose an option '


class CompleteInput(Command):
    character = '\r'
    hint = ''
    description = 'Send your input'
    changes_window = True


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
