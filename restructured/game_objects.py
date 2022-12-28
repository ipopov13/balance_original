import commands
import console
import config
# TODO: Split the objects in modules by level of abstraction:
#  GameObject/Container <- Race|Item|Creature|world|etc. <- Game

races = []


class GameObject:
    def __init__(self, name=None, icon='.', color=console.fg.black,
                 description='(empty)', sort_key=0):
        self.name = name
        self._icon = icon
        self.color = color
        self._description = description
        self.sort_key = sort_key

    @property
    def description(self):
        return self._description

    @property
    def icon(self):
        return self.color + self._icon + console.fx.end

    @staticmethod
    def commands() -> dict:
        return {}

    @staticmethod
    def data() -> str:
        return '(empty)'


class Container(GameObject):
    def __init__(self, width: int, height: int, **kwargs):
        super().__init__(**kwargs)
        self._width = width
        self._height = height
        self._contents: list[GameObject] = []

    def _data_prep(self) -> None:
        """
        Adjust the data before presentation
        Can be overridden by subclasses for extra functionality
        """
        pass
        # TODO: items get the correct sort_key when being added into a physical container.
        #  The key is their location inside the container!

    def data(self) -> str:
        self._data_prep()
        rows = [[c.icon for c in self._contents[start:start + self._width]]
                for start in range(0, len(self._contents), self._width)]
        rows = [''.join(row) for row in rows]
        return '\n'.join(rows)


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
        self._character_location = None
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
        self.world = World()
        self._character_location = self.world[0][0]

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

    def get_character_hud(self) -> str:
        # TODO: Add active mode, current interaction target name and health/durability gauge (without
        #  numbers, also applicable to work-target terrains),
        #  target location (chosen on map, hinted with Travelling: West-NW)
        hp_gauge = self._format_gauge(self.character.hp, self.character.max_hp, config.hp_color)
        mana_gauge = self._format_gauge(self.character.mana, self.character.max_mana, config.mana_color)
        energy_gauge = self._format_gauge(self.character.energy, self.character.max_energy, config.energy_color)
        load_gauge = self._format_gauge(self.character.load, self.character.max_load, config.load_color)
        hud = f'HP [{hp_gauge}] | Mana [{mana_gauge}] | Energy [{energy_gauge}] | Load [{load_gauge}]'
        return hud

    @staticmethod
    def _format_gauge(current_stat, max_stat, color) -> str:
        raw_gauge = f'{current_stat}/{max_stat}'.center(10, ' ')
        percentage_full = int((current_stat / max_stat) * 10)
        colored_gauge = color + raw_gauge[:percentage_full] + console.fx.end + raw_gauge[percentage_full:]
        return colored_gauge

    def get_area_view(self) -> list[str]:
        return self._character_location.data()


# TODO: Implement Terrains
class Terrain(GameObject):
    def __init__(self, passable: bool = True, exhaustion_factor: int = 0, **kwargs):
        super().__init__(**kwargs)
        self.passable = passable
        self.exhaustion_factor = exhaustion_factor


grass = Terrain(color=console.fg.green, description='grass')


def set_neighbors(spot, neighbor_list: list, row_length: int):
    adjacency_map = {spot.sort_key - 1: 'w', spot.sort_key + 1: 'e',
                     spot.sort_key - row_length - 1: 'nw',
                     spot.sort_key - row_length: 'n',
                     spot.sort_key - row_length + 1: 'ne',
                     spot.sort_key + row_length - 1: 'sw',
                     spot.sort_key + row_length: 's',
                     spot.sort_key + row_length + 1: 'se'}
    for neighbor in neighbor_list:
        if type(neighbor) != type(spot):
            raise TypeError(f"Wrong type of neighbor {type(neighbor)} passed"
                            f" for spot {type(spot)}@{spot.sort_key}!")
        adjacency = adjacency_map.get(neighbor.sort_key, None)
        if adjacency is None:
            raise ValueError(f'Wrong neighbor {neighbor.sort_key} passed to {type(spot)} at position'
                             f'{spot.sort_key}!')
        else:
            if spot.neighbors[adjacency] is None:
                spot.neighbors[adjacency] = neighbor
            else:
                raise ValueError(f'Two neighbors with the same adjacency {adjacency}/{neighbor.sort_key}'
                                 f' passed to {type(spot)}@{spot.sort_key}!')


class Tile(Container):
    def __init__(self, terrain: Terrain, sort_key: int = 0):
        super().__init__(height=3, width=3, sort_key=sort_key)
        self.terrain = terrain
        self.creature: Character = None
        self.neighbors = {'nw': None, 'n': None, 'ne': None,
                          'w': None, 'self': self, 'e': None,
                          'sw': None, 's': None, 'se': None}

    @property
    def description(self):
        return self.terrain.description

    @property
    def icon(self):
        if self.creature is not None:
            return self.creature.icon
        return self.terrain.icon


# TODO: Structures generation
# TODO: Tile neighboring
# TODO: NPCs
class Location(Container):
    def __init__(self, sort_key: int):
        super().__init__(height=config.location_height, width=config.location_width, sort_key=sort_key)
        self._contents: list[Tile] = []

    def _data_prep(self) -> None:
        if not self._contents:
            self._generate_tiles()

    def _generate_tiles(self) -> None:
        self._contents = [Tile(terrain=grass, sort_key=i) for i in range(self._width * self._height)]


# TODO: PoI selection and randomization
# TODO: Rolls the environment stats on init
# TODO: Inits the locations with the PoI/force/stats (handles gradients)
class Region(Container):
    def __init__(self, sort_key: int):
        super().__init__(height=config.region_size, width=config.region_size, sort_key=sort_key)
        self._contents: list[Location] = []

    @property
    def contents(self):
        if not self._contents:
            self._generate_locations()
        return self._contents

    def _generate_locations(self) -> None:
        self._contents = [Location(sort_key=i) for i in range(self._width * self._height)]

    def __getitem__(self, item: int):
        if not self.contents:
            self._generate_locations()
        if not isinstance(item, int):
            raise TypeError(f'Region location index must be int, not {type(item)} ({item})')
        return self.contents[item]


# TODO: Randomize forces and pass to regions on init
class World(Container):
    def __init__(self):
        super().__init__(height=config.world_size, width=config.world_size)
        self._contents: list[Region] = [Region(sort_key=i) for i in range(self._width * self._height)]

    def __getitem__(self, item: int):
        if not isinstance(item, int):
            raise TypeError(f'World location index must be int, not {type(item)} ({item})')
        return self._contents[item]


if __name__ == '__main__':
    l = Location(0)
    data = l.data()
    print(len(l.data()))
    print([data[:30]])
