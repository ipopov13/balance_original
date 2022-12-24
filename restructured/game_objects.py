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


class Game:
    def __init__(self):
        self.character = Character()

    def set_character_name(self, player_input):
        self.character.name = player_input
