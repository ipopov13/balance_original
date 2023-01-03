from typing import Optional
import random
import commands
import console
import config

# TODO: Split the objects in modules by level of abstraction:
#  GameObject/Container <- Race|Item|Creature|world|etc. <- Game

races = []
NATURE_FORCE = 'Nature'
CHAOS_FORCE = 'Chaos'
ORDER_FORCE = 'Order'
force_colors = {NATURE_FORCE: config.nature_color,
                CHAOS_FORCE: config.chaos_color,
                ORDER_FORCE: config.order_color}
COLD_CLIMATE = 'Cold'
TEMPERATE_CLIMATE = 'Temperate'
HOT_CLIMATE = 'Hot'


class GameObject:
    def __init__(self, name=None, icon='.', color=console.fg.black,
                 description='(empty)', sort_key=0):
        self._name = name or description
        self.raw_icon = icon
        self.color = color
        self._description = description
        self.sort_key = sort_key

    @property
    def name(self):
        return self._name

    @property
    def description(self):
        return self._description

    @property
    def icon(self):
        return self.color + self.raw_icon + console.fx.end

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
        self._contents: list[list] = []

    @property
    def contents(self):
        self._data_prep()
        return self._contents

    def _data_prep(self) -> None:
        """
        Adjust the _contents before presentation
        Can be overridden by subclasses for extra functionality
        """
        pass
        # TODO: items get the correct sort_key when being added into a physical container.
        #  The key is their location inside the container!

    def data(self) -> str:
        rows = [[c.icon for c in row]
                for row in self.contents]
        rows = [''.join(row) for row in rows]
        return '\n'.join(rows)


class Item(GameObject):
    pass


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


class Creature(GameObject):
    # TODO: Creatures have goals and they ask the Location for the path to the closest
    #  Tile that satisfies the goal
    def __init__(self, race=None, **kwargs):
        super().__init__(**kwargs)
        self.race = race
        self.strength = 5
        self.dexterity = 5
        self.will = 5
        self.endurance = 5
        # TODO: Add ageing for NPCs here between the stats and the sub-stats
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
    Keep the game state: All elements that can change their own state (Creatures, effects, crops, etc.)
    States:
    """
    welcome_state = 'welcome'
    new_game_state = 'starting_new_game'
    loading_state = 'loading_existing_game'
    character_name_substate = 'getting_character_name'
    race_selection_substate = 'character_race_selection'
    playing_state = 'playing'
    # TODO: Implement subs: inventory, equipment, open_container, etc.
    scene_substate = 'game_scene'
    map_substate = 'world_map'
    high_score_state = 'high_score'
    ended_state = 'ended'
    races = races

    def __init__(self):
        self.character: Optional[Creature] = None
        self._current_location: Optional[Location] = None
        self.character_name: Optional[str] = None
        self._creature_coords: dict[Creature, tuple[int, int]] = {}
        self.world: Optional[World] = None
        self.state: str = Game.welcome_state
        self.substate: Optional[str] = None

    def set_character_race(self, character_race):
        self.character = Creature(name=self.character_name, race=character_race,
                                  description='You are standing here.', color=console.fg.default,
                                  icon='@')
        self._creature_coords[self.character] = (0, 0)
        self._current_location = self.world.get_location(self._creature_coords[self.character])
        self._current_location.add_creature(self.character, self._creature_coords[self.character])
        self.state = Game.playing_state
        self.substate = Game.scene_substate

    def set_character_name(self, character_name):
        if self.state is Game.new_game_state:
            self.character_name = character_name
            self.substate = Game.race_selection_substate
        elif self.state is Game.loading_state:
            self._load_saved_game(character_name)
            self.state = Game.playing_state
            self.substate = Game.scene_substate
        return True

    def commands(self) -> dict:
        # TODO: Offer different commands depending on state
        if self.state is Game.welcome_state:
            return {commands.NewGame(): self._new_game,
                    commands.LoadGame(): self._initiate_load}
        elif self.state is Game.playing_state and self.substate is Game.scene_substate:
            return {commands.Move(): self._move_character,
                    commands.Map(): self._open_map}
        elif self.state is Game.playing_state and self.substate is Game.map_substate:
            return {commands.Move(): self._move_map_focus,
                    commands.Close(): self._close_map}

    def _close_map(self, _) -> bool:
        self.substate = Game.scene_substate
        return True

    def _move_map_focus(self, _):
        raise NotImplementedError

    def _open_map(self, _) -> bool:
        self.substate = Game.map_substate
        return True

    def _move_character(self, direction):
        self._move_creature(self.character, direction)
        return True

    def _new_game(self, _):
        self.world = World()
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

    @staticmethod
    def data() -> str:
        return r''' ___      _   _         _   _    _   ___   ____
|   \    / |  |        / |  |\   |  /   \ |
|___/   /  |  |       /  |  | \  |  |     |___
|   \  /---|  |      /---|  |  \ |  |     |
|___/ /    |  |___| /    |  |   \|  \___/ |____

                    ver 0.7
                  Ivan Popov'''

    def get_current_location_name(self) -> str:
        return self._current_location.name

    def get_character_hud(self) -> str:
        # TODO: Add active mode, current interaction target name and health/durability gauge (without
        #  numbers, also applicable to work-target terrains),
        #  target location (chosen on map, hinted with Travelling: West-NW)
        hp_gauge = self._format_gauge(self.character.hp, self.character.max_hp, config.hp_color)
        mana_gauge = self._format_gauge(self.character.mana, self.character.max_mana, config.mana_color)
        energy_gauge = self._format_gauge(self.character.energy, self.character.max_energy, config.energy_color)
        load_gauge = self._format_gauge(self.character.load, self.character.max_load, config.load_color)
        hud = f'HP [{hp_gauge}] | Mana [{mana_gauge}] | Energy [{energy_gauge}] | Load [{load_gauge}]\n' \
              f'{self._current_location._forces}'
        return hud

    @staticmethod
    def _format_gauge(current_stat, max_stat, color) -> str:
        raw_gauge = f'{current_stat}/{max_stat}'.center(10, ' ')
        percentage_full = int((current_stat / max_stat) * 10)
        colored_gauge = color + raw_gauge[:percentage_full] + console.fx.end + raw_gauge[percentage_full:]
        return colored_gauge

    def get_area_view(self) -> str:
        # TODO: The Game gets the 8 neighbor locations and displays the Tiles to make the scene consistent
        #     when there is impassable Terrain in the neighbor Location
        return self._current_location.data()

    def get_character_position_in_location(self) -> tuple[int, int]:
        return self._creature_coords[self.character][0] % config.location_height, \
            self._creature_coords[self.character][1] % config.location_width

    def get_world_data(self) -> str:
        return self.world.data()

    def get_region_data(self, coords: tuple[int, int] = None) -> str:
        if coords is None:
            coords = self._creature_coords[self.character]
        return self.world.get_region_data(coords)

    def _move_creature(self, creature: Creature, direction: str) -> None:
        # TODO: Once the character moves to a new location,
        #     the Game sends the old Location to the World for saving and requests a new one.
        creature_location = self.world.get_location(self._creature_coords[creature])
        if creature_location is not self._current_location:
            raise ValueError(f'Creatures outside of current location should not be moving! '
                             f'{creature.name} {self._creature_coords[creature]}')
        old_coords = self._creature_coords[creature]
        new_coords = self._calculate_new_position(self._creature_coords[creature], direction)
        # TODO: Implement creature check at new coords and interaction here
        old_location = self._current_location
        new_location = self.world.get_location(new_coords)
        if new_location.can_ocupy(creature, new_coords):
            self._creature_coords[creature] = new_coords
            old_location.remove_creature(old_coords)
            self._current_location = new_location
            new_location.add_creature(creature, new_coords)
        elif creature is self.character:
            # TODO: Implement log message describing why the move is impossible
            pass

    def _calculate_new_position(self, old_pos: tuple[int, int], direction: str) -> tuple[int, int]:
        row, column = old_pos
        if direction in '789':
            row -= 1
            if row == -1:
                row = self.world.size[0] - 1
        elif direction in '123':
            row += 1
            if row == self.world.size[0]:
                row = 0
        if direction in '147':
            column -= 1
            if column == -1:
                column = self.world.size[1] - 1
        elif direction in '369':
            column += 1
            if column == self.world.size[1]:
                column = 0
        return row, column


# TODO: Add Terrains
class Terrain(GameObject):
    def __init__(self, passable: bool = True, exhaustion_factor: int = 0, **kwargs):
        super().__init__(**kwargs)
        self.passable = passable
        self.exhaustion_factor = exhaustion_factor

    def is_passable_for(self, creature):
        return self.passable


grass = Terrain(color=console.fg.lightgreen, description='grass')
ashes = Terrain(color=console.fg.lightblack, description='ashes')
dirt = Terrain(color=config.brown_fg_color, description='dirt')
snow = Terrain(color=console.fg.white, description='snow')
sand = Terrain(color=console.fg.yellow, description='sand')
old_pavement = Terrain(color=console.fg.lightyellow, description='old pavement')
ice = Terrain(color=console.fg.lightblue, description='ice')
flowers = Terrain(color=console.fg.purple, description='flowers', icon='*')
bones = Terrain(color=console.fg.lightwhite, description='bones', icon='~')
water = Terrain(color=console.fg.blue, description='water', icon='~')
swamp = Terrain(color=console.fg.lightgreen, description='swamp', icon='~')
poisoned_water = Terrain(color=console.fg.lightblack, description='poisoned water', icon='~')
tree = Terrain(color=console.fg.lightgreen, description='tree', icon='T')
jungle = Terrain(color=console.fg.green, description='tree', icon='T', passable=False)
bush = Terrain(color=console.fg.lightgreen, description='bush', icon='#')
lichen_clump = Terrain(color=console.fg.lightgreen, description='lichen clump', icon='o')
dead_tree = Terrain(color=console.fg.lightblack, description='dead tree', icon='T')
frozen_tree = Terrain(color=console.fg.lightblue, description='frozen tree', icon='T')
rocks = Terrain(color=console.fg.lightblack, description='rocks', icon='%', passable=False)
mossy_rock = Terrain(color=console.fg.lightgreen, description='mossy rock', icon='%', passable=False)
ice_block = Terrain(color=console.fg.lightblue, description='ice block', icon='%', passable=False)
ruined_wall = Terrain(color=config.brown_fg_color, description='ruined wall', icon='#', passable=False)
lava = Terrain(color=console.fg.red, description='lava', icon='~', passable=False)
base_force_terrains = {
    COLD_CLIMATE: {NATURE_FORCE: [snow, frozen_tree, tree],
                   CHAOS_FORCE: [ice, dead_tree, swamp],
                   ORDER_FORCE: [snow, dirt, rocks]},
    TEMPERATE_CLIMATE: {NATURE_FORCE: [grass, tree, bush],
                        CHAOS_FORCE: [ashes, swamp, dead_tree],
                        ORDER_FORCE: [dirt, rocks]},
    HOT_CLIMATE: {NATURE_FORCE: [sand, bush],
                  CHAOS_FORCE: [sand, dead_tree],
                  ORDER_FORCE: [sand, rocks]}}
filler_terrains = {
    COLD_CLIMATE: {NATURE_FORCE: snow,
                   CHAOS_FORCE: ice,
                   ORDER_FORCE: snow},
    TEMPERATE_CLIMATE: {NATURE_FORCE: grass,
                        CHAOS_FORCE: ashes,
                        ORDER_FORCE: dirt},
    HOT_CLIMATE: {NATURE_FORCE: sand,
                  CHAOS_FORCE: sand,
                  ORDER_FORCE: sand}}
flavor_terrains = {
    COLD_CLIMATE: {NATURE_FORCE: [flowers, mossy_rock, lichen_clump],
                   CHAOS_FORCE: [bones, ice_block],
                   ORDER_FORCE: [ruined_wall, old_pavement]},
    TEMPERATE_CLIMATE: {NATURE_FORCE: [flowers, mossy_rock],
                        CHAOS_FORCE: [bones, lava],
                        ORDER_FORCE: [ruined_wall, old_pavement]},
    HOT_CLIMATE: {NATURE_FORCE: [jungle, flowers],
                  CHAOS_FORCE: [bones, lava],
                  ORDER_FORCE: [ruined_wall, old_pavement]}}


class Tile(Container):
    def __init__(self, terrain: Terrain):
        super().__init__(height=3, width=3)
        self.terrain = terrain
        self.creature: Optional[Creature] = None

    @property
    def contents(self) -> list[list[Item]]:
        self._data_prep()
        return self._contents

    @property
    def description(self):
        return self.terrain.description

    @property
    def icon(self):
        if self.creature is not None:
            return self.creature.icon
        return self.terrain.icon


# TODO: Structures&NPCs generation
# TODO: Tile neighboring
# TODO: Answer calls from the NPCs for the path to their closest goal (e.g. rock to mine, character to attack)
class Location(Container):
    """
    Generates the terrain data
    Keeps the stateless data about the location: terrain, items
    Provides Line-of-sight information
    Provides pathfinding
    """

    def __init__(self, top_left: tuple[int, int] = (0, 0), forces: dict[str, int] = None,
                 main_terrain: Terrain = None, climate: str = None, region_name: str = None):
        self._contents: list[list[Tile]] = []
        self._top_left = top_left
        self._forces = forces
        self._terrains: list[Terrain] = []
        self._terrain_weights: list[float] = []
        self._region_name = region_name
        self._flavor: Optional[Terrain] = None
        self._select_terrains(base=main_terrain, climate=climate)
        super().__init__(height=config.location_height, width=config.location_width,
                         icon=self._flavor.raw_icon, color=self._flavor.color)

    def _main_force(self):
        rev_forces = {v: k for k, v in self._forces.items()}
        return rev_forces[max(rev_forces)]

    def _select_terrains(self, base: Terrain, climate: str) -> None:
        # TODO: Fill 64.5% with fillers based on forces, 35% with base + 1 other per force based on forces,
        #  and 0.5% with a flavor chosen on forces
        descriptive_fraction = 40
        flavor_fraction = 1
        base_weight = descriptive_fraction * self._forces[self._main_force()] / 100
        # Add a flavor terrain
        forces = list(self._forces.keys())
        force_weights = [self._forces[f] for f in forces]
        random_force = random.choices(forces, weights=force_weights)[0]
        flavor = random.choice(flavor_terrains[climate][random_force])
        # Add filler terrain based on climate & force
        filler = filler_terrains[climate][self._main_force()]
        filler_weight = 100 - base_weight - flavor_fraction
        self._terrains = [filler, base, flavor]
        self._terrain_weights = [filler_weight, base_weight, flavor_fraction]
        self._flavor = flavor

    @property
    def name(self) -> str:
        # TODO: Implement the area name as the area name + the region name, colored depending on the force.
        #  The name implementation can be provided by the area (if it knows the region object)
        #  Example: "Village of Stow, Woods of Despair"
        #  The area has a name only if it has something to show on the map (resource, artifact, settlement),
        #  otherwise it only carries the name of the region
        return f'{str(self._top_left)}, {self._region_name}'

    def _data_prep(self) -> None:
        if not self._contents:
            self._contents = [[Tile(terrain=random.choices(self._terrains, weights=self._terrain_weights)[0])
                               for _ in range(self._width)]
                              for _ in range(self._height)]

    @property
    def contents(self) -> list[list[Tile]]:
        self._data_prep()
        return self._contents

    def add_creature(self, creature: Creature, coords: tuple[int, int]) -> None:
        self._tile_at(coords).creature = creature

    def remove_creature(self, coords: tuple[int, int]) -> None:
        tile = self._tile_at(coords)
        if tile.creature is None:
            raise ValueError(f'Tile at coords {coords} has no creature!')
        tile.creature = None

    def can_ocupy(self, creature: Creature, coords: tuple[int, int]) -> bool:
        return self._tile_at(coords).terrain.is_passable_for(creature)

    def _tile_at(self, coords: tuple[int, int]) -> Tile:
        return self.contents[coords[0] - self._top_left[0]][coords[1] - self._top_left[1]]

    def data(self) -> str:
        rows = [[c.icon for c in row]
                for row in self.contents]
        rows = [''.join(row) for row in rows]
        return '\n'.join(rows)


# TODO: Rolls the base terrains on init
# TODO: PoI selection and randomization
# TODO: Init the locations with the PoI/force/base terrains (handles gradients)
class Region(Container):
    height_in_tiles = config.region_size * config.location_height
    width_in_tiles = config.region_size * config.location_width
    region_names = {COLD_CLIMATE: {snow: 'Frost lands',
                                   frozen_tree: 'Frozen forests',
                                   tree: 'Winter woods',
                                   ice: 'Ice fields',
                                   dead_tree: 'Icy deadwood',
                                   swamp: 'Frozen swamps',
                                   dirt: 'Snowy fields',
                                   rocks: 'Snowy mountains'},
                    TEMPERATE_CLIMATE: {grass: 'Plains',
                                        tree: 'Forest',
                                        bush: 'Bushland',
                                        ashes: 'Wasteland',
                                        swamp: 'Marshlands',
                                        dead_tree: 'Deadwood',
                                        dirt: 'Fields',
                                        rocks: 'Mountains'},
                    HOT_CLIMATE: {sand: 'Desert',
                                  bush: 'Dry bushland',
                                  dead_tree: 'Wasted deadwoods',
                                  rocks: 'Rocky dunes'}}

    def __init__(self, top_left: tuple[int, int], main_force: str, climate: str, suffix: str = ' of tests'):
        self._top_left = top_left
        self._main_force = main_force
        self._climate = climate
        self._main_terrain: Terrain = random.choice(base_force_terrains[self._climate][self._main_force])
        raw_name = f'{Region.region_names[self._climate][self._main_terrain]} {suffix}'
        name = f'{force_colors[self._main_force]}{raw_name}{console.fx.end}'
        super().__init__(height=config.region_size, width=config.region_size,
                         name=name, icon=self._main_terrain.raw_icon, color=self._main_terrain.color)

    def _data_prep(self) -> None:
        if not self._contents:
            self._generate_locations()

    @property
    def contents(self) -> list[list[Location]]:
        self._data_prep()
        return self._contents

    def _generate_locations(self) -> None:
        self._contents = [[Location(top_left=self._get_location_top_left(row, column),
                                    forces=self._calculate_forces(row, column),
                                    main_terrain=self._main_terrain,
                                    climate=self._climate,
                                    region_name=self.name)
                           for column in range(self._width)] for row in range(self._height)]

    def _calculate_forces(self, row: int, column: int) -> dict[str, int]:
        forces = {NATURE_FORCE: 33, CHAOS_FORCE: 33, ORDER_FORCE: 33}
        forces[self._main_force] += 1
        gradient = config.region_size // 2
        try:
            scaling_factor = (gradient - max(abs(gradient - row), abs(gradient - column))) * (1 / gradient)
        except ZeroDivisionError:
            scaling_factor = 1
        adjustment = int(66 * scaling_factor)
        for force in forces:
            if force == self._main_force:
                forces[force] += adjustment
            else:
                forces[force] -= adjustment // 2
        return forces

    def _get_location_top_left(self, row: int, column: int) -> tuple[int, int]:
        location_top_left_row = self._top_left[0] + row * config.location_height
        location_top_left_column = self._top_left[1] + column * config.location_width
        return location_top_left_row, location_top_left_column

    def get_location(self, coords: tuple[int, int]) -> Location:
        local_row_in_tiles = coords[0] - self._top_left[0]
        local_column_in_tiles = coords[1] - self._top_left[1]
        location_row = local_row_in_tiles // config.location_height
        location_column = local_column_in_tiles // config.location_width
        return self.contents[location_row][location_column]


# TODO: Randomize forces and pass to regions on init
class World(Container):
    region_suffixes = {CHAOS_FORCE: """of Blood
of Bone
of Darkness
of Decay
of Desolation 
of Despair
of the Fang
of Fear
of Fog
of the Ghost
of Graves
of Horror
of lost souls
of no return
of Pain
of Poison
of Rot
of Ruin
of Screaming
of Shackles
of the Skull
of Suffering 
of the Dead
of the Festering
of the Tyrant
of the Vampire 
of the Worm
of the Zombie""".split('\n'),
                       ORDER_FORCE: """of Bread
of Beauty
of the Bell
of the Bridge
of Bronze
of the Crafter
of the Diamond
of the Explorer
of Gold
of the Hunter
of Iron
of the King
of the Mason
of the Miner
of the Plow
of Queen's grace
of Roads
of the Scholar
of Silver
of the Smith
of the Soldier
of Sorcery
of Steel
of the Sword
of the Tailor
of the Tomb
of the Trader
of White
of Wine""".split('\n'),
                       NATURE_FORCE: """of the Bear
of the Bee
of the Bird
of Bloom
of Calm
of Clay
of the Dragon
of Feathers
of Flowers
of Green
of Leaves
of the Lion
of Moss
of the Pig
of Roots
of Scales
of Silence
of the Snake
of Stone
of the Storm
of Streams
of Sunlight
of the Earth
of Thunder 
of the Tiger
of Whispers
of Wings
of the Wolf""".split('\n')}

    def __init__(self):
        super().__init__(height=config.world_size, width=config.world_size)
        forces = [NATURE_FORCE, ORDER_FORCE, CHAOS_FORCE] * (config.world_size ** 2 // 3 + 1)
        random.shuffle(forces)
        self._contents: Optional[list[list[Region]]] = []
        suffixes = World.region_suffixes.copy()
        for f in suffixes:
            random.shuffle(suffixes[f])
        for row in range(self._height):
            region_list = []
            for column in range(self._width):
                main_force = forces.pop()
                climate = random.choice([COLD_CLIMATE, TEMPERATE_CLIMATE, HOT_CLIMATE])
                suffix = suffixes[main_force].pop()
                region_list.append(Region(top_left=self._get_region_top_left(row, column),
                                          main_force=main_force,
                                          climate=climate,
                                          suffix=suffix))
            self._contents.append(region_list[:])

    @staticmethod
    def _get_region_top_left(row: int, column: int) -> tuple[int, int]:
        region_top_left_row = row * Region.height_in_tiles
        region_top_left_column = column * Region.width_in_tiles
        return region_top_left_row, region_top_left_column

    def _get_region_from_absolute_coords(self, coords: tuple[int, int]) -> Region:
        row = coords[0] // Region.height_in_tiles
        column = coords[1] // Region.width_in_tiles
        try:
            region = self.contents[row][column]
        except IndexError:
            raise IndexError(f'Wrong region coords ({row}, {column}) from absolute coords {coords}!')
        return region

    def get_region_data(self, coords: tuple[int, int]) -> str:
        region = self._get_region_from_absolute_coords(coords)
        return region.data()

    def get_location(self, coords: tuple[int, int]) -> Location:
        region = self._get_region_from_absolute_coords(coords)
        return region.get_location(coords)

    @property
    def contents(self) -> list[list[Region]]:
        self._data_prep()
        return self._contents

    @property
    def size(self) -> tuple[int, int]:
        return config.world_size * config.region_size * config.location_height, \
               config.world_size * config.region_size * config.location_width


if __name__ == '__main__':
    location = Location((0, 0), {}, grass)
    data = location.data()
    print(len(location.data()))
    print([data[:30]])
