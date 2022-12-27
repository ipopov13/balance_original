import commands
import console
import config

races = []


class GameObject:
    def __init__(self, name=None, icon='@', color=console.fg.default,
                 description='(empty GameObj description)', sort_key=0):
        self.name = name
        self.icon = icon
        self.color = color
        self.description = description
        self.sort_key = sort_key

    @staticmethod
    def commands() -> dict:
        return {}

    @staticmethod
    def data() -> str:
        return '(empty object data)'


class Race(GameObject):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        races.append(self)


human_race = Race(name='Human',
                  icon='H',
                  color=config.order_color,
                  description='Explorers and treasure seekers, the human race combines the primal need '
                              'of discovery with the perseverance that gave birth to all great empires.',
                  sort_key=0)
dwarf_race = Race(name='Dwarf',
                  icon='D',
                  color=config.order_color,
                  description='Masters of the forge, they are drawn down into the depths of the world by '
                              'an ancient instinct that rivals the bravery of human explorers.',
                  sort_key=1)
gnome_race = Race(name='Gnome',
                  icon='G',
                  color=config.order_color,
                  description='The only race that views rocks as living things,'
                              ' gnomes are friendly and easygoing.',
                  sort_key=2)
elf_race = Race(name='Elf',
                icon='E',
                color=config.order_color,
                description='Expert mages and librarians, the elves have given the world'
                            ' a lot of legendary heroes.',
                sort_key=3)
orc_race = Race(name='Orc',
                icon='O',
                color=config.chaos_color,
                description='The most aggressive of races, orcs crave combat above all else.'
                            ' They always keep a spare weapon around, just in case.',
                sort_key=4)
troll_race = Race(name='Troll',
                  icon='T',
                  color=config.chaos_color,
                  description="Finding a tasty rock to eat makes a troll's day. Having "
                              "someone to throw a rock at is a bonus that only a troll can appreciate in full.",
                  sort_key=5)
goblin_race = Race(name='Goblin',
                   icon='G',
                   color=config.chaos_color,
                   description="For a goblin, everything can come in handy one day. They are"
                               " legendary pilferers and pillagers, and leave no one, and nothing, behind.",
                   sort_key=6)
kraken_race = Race(name='Kraken',
                   icon='K',
                   color=config.chaos_color,
                   description="Descendants of deep sea monsters, the kraken have learned to "
                               "reap even the most disgusting of water dwellers for useful substances.",
                   sort_key=7)
imp_race = Race(name='Imp',
                icon='I',
                color=config.chaos_color,
                description="Fire burns in an imp's veins and dances over their fingers."
                            " To burn is to feel alive!",
                sort_key=8)
dryad_race = Race(name='Dryad',
                  icon='D',
                  color=config.nature_color,
                  description="The kin of plants, dryads are champions of the forest. They give"
                              " trees their all and received undying love in return.",
                  sort_key=9)
shifter_race = Race(name='Shifter',
                    icon='S',
                    color=config.nature_color,
                    description="A shifter can easily pass as a human if they cut their talon-like nails "
                                "and keep their totemic tattoos hidden. They rarely do.",
                    sort_key=10)
water_elemental_race = Race(name='Water Elemental',
                            icon='W',
                            color=config.nature_color,
                            description="To make other living beings see the beauty of water, elementals "
                                        "turn it into art, home, and sustenance.",
                            sort_key=11)
fay_race = Race(name='Fay',
                icon='F',
                color=config.nature_color,
                description="The fay are born from the natural magic of the world, and "
                            "they have developed methods to manipulate it. Their ability to "
                            "trespass into the dreams of others is an insignificant side effect.",
                sort_key=12)


class Character(GameObject):
    def __init__(self, race=None, **kwargs):
        super().__init__(**kwargs)
        self.race = race
        self.strength = 5
        self.dexterity = 5
        self.will = 5
        self.endurance = 5
        # TODO: Add ageing for NPCs here between the stats and the substats
        self.hp = self.max_hp
        self.mana = self.max_mana
        self.energy = self.max_energy
        self.load = 0

    @property
    def max_hp(self):
        return self.strength + 2 * self.endurance

    @property
    def max_mana(self):
        return self.will * 10

    @property
    def max_energy(self):
        return self.endurance * 10

    @property
    def max_load(self):
        return self.strength * 5


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
    races = races

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

    @property
    def current_area_name(self) -> str:
        # TODO: Implement the area name as the area name + the region name, colored depending on the force.
        #  The name implementation can be provided by the area (if it knows the region object)
        #  Example: "Village of Stow, Woods of Despair"
        #  The area has a name only if it has something to show on the map (resource, artifact, settlement),
        #  otherwise it only carries the name of the region
        return '(area), (region)'

    def get_character_hud(self) -> list[str]:
        hp_gauge = self._format_gauge(self.character.hp, self.character.max_hp, config.hp_color)
        mana_gauge = self._format_gauge(self.character.mana, self.character.max_mana, config.mana_color)
        energy_gauge = self._format_gauge(self.character.energy, self.character.max_energy, config.energy_color)
        load_gauge = self._format_gauge(self.character.load, self.character.max_load, config.load_color)
        hud = f'HP [{hp_gauge}] | Mana [{mana_gauge}] | Energy [{energy_gauge}] | Load [{load_gauge}]'
        return [hud]

    @staticmethod
    def _format_gauge(current_stat, max_stat, color) -> str:
        raw_gauge = f'{current_stat}/{max_stat}'.center(10, ' ')
        percentage_full = int((current_stat / max_stat) * 10)
        print(current_stat, max_stat, percentage_full)
        input()
        colored_gauge = color + raw_gauge[:percentage_full] + console.fx.end + raw_gauge[percentage_full:]
        return colored_gauge

    def get_area_view(self) -> list[str]:
        # TODO: Implement area view
        return [''] * 21


if __name__ == '__main__':
    print(human_race.sort_key)
