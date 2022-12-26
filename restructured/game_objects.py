import commands


class GameObject:
    def __init__(self, name=None, icon='@', description='(empty GameObj description)', sort_key=0):
        self.name = name
        self.icon = icon
        self.description = description
        self.sort_key = sort_key

    @staticmethod
    def commands() -> dict:
        return {}

    @staticmethod
    def data() -> str:
        return '(empty object data)'


human_race = GameObject(name='Human',
                        icon='H',
                        description='Explorers and treasure seekers, the human race combines the primal need '
                                    'of discovery with the perseverance that gave birth to all great empires.',
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
    def __init__(self, race=None, **kwargs):
        super().__init__(**kwargs)
        self.race = race


class Game:
    """
    Keep the game state
    States:
    """
    welcome_state = 'welcome'
    new_game_state = 'starting_new_game'
    loading_state = 'loading_existing_game'
    character_name_substate = 'getting_character_name'
    race_selection_substate = 'character_race_selection'
    playing_state = 'playing'
    # TODO: Implement subs: scene, inventory, equipment, open_container, open_map, etc.
    scene_substate = 'game_scene'
    high_score_state = 'high_score'
    ended_state = 'ended'
    races = [human_race, gnome_race, elf_race, dwarf_race]

    def __init__(self):
        self.character = None
        self.world = None
        self.state = Game.welcome_state
        self.substate = None

    def set_character_race(self, character_race):
        self.character.race = character_race
        self.state = Game.playing_state
        self.substate = Game.scene_substate

    def set_character_name(self, character_name):
        if self.state is Game.new_game_state:
            self.character = Character(name=character_name, description='You are standing here.')
            self.substate = Game.race_selection_substate
        elif self.state is Game.loading_state:
            self._load_saved_game(character_name)
            self.state = Game.playing_state
            self.substate = Game.scene_substate
        return True

    def commands(self) -> dict:
        return {commands.NewGame(): self._new_game,
                commands.LoadGame(): self._initiate_load}

    def _new_game(self, _):
        self._create_world()
        self.state = Game.new_game_state
        self.substate = Game.character_name_substate
        return True

    def _initiate_load(self, _):
        self.state = Game.loading_state
        self.substate = Game.character_name_substate
        return True

    def _load_saved_game(self, name):
        # TODO: Implement loading
        raise NotImplementedError("Implement loading games!")

    def _create_world(self):
        # TODO: Implement world creation
        self.world = 1

    @staticmethod
    def data() -> str:
        return r''' ___      _   _         _   _    _   ___   ____
|   \    / |  |        / |  |\   |  /   \ |
|___/   /  |  |       /  |  | \  |  |     |___
|   \  /---|  |      /---|  |  \ |  |     |
|___/ /    |  |___| /    |  |   \|  \___/ |____

                    ver 0.7
                  Ivan Popov'''
