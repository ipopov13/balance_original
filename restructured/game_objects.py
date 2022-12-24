class GameObject:
    def __init__(self, name='', icon='@', description='(empty GameObj description)', sort_key=0):
        self.name = name
        self.icon = icon
        self.description = description
        self.sort_key = sort_key


human_race = GameObject(name='Human',
                        icon='H',
                        description='Explorers and treasure seekers, the human race combines the primal need '
                                    'of discovery with the perseverance that has created all great empires.',
                        sort_key=0)
dwarf_race = GameObject(name='Dwarf',
                        icon='D',
                        description='Masters of the forge, they are drawn down into the depths of the world by '
                                    'an ancient instinct that rivals the bravery of human explorers.',
                        sort_key=1)
gnome_race = GameObject(name='Gnome',
                        icon='G',
                        description='The only race that views rocks as living things,'
                                    ' gnomes are friendly and easygoing.',
                        sort_key=2)
elf_race = GameObject(name='Elf',
                      icon='E',
                      description='Expert mages and librarians, the elves have given the world'
                                  ' a lot of legendary heroes.',
                      sort_key=3)


class Character(GameObject):
    def __init__(self):
        super().__init__()
        self.race = None

    def data(self) -> str:
        if self.name == '':
            return ''
        return '(empty character data)'


class Game:
    races = [human_race, gnome_race, elf_race, dwarf_race]

    def __init__(self):
        self.character = Character()

    def start_game(self, character_name):
        self.character.name = character_name

    def set_character_race(self, race):
        self.character.race = race
