from typing import Optional
import random
import commands
import console
import config

# TODO: Split the objects in modules by level of abstraction:
#  GameObject/Container <- SentientSpecies|Item|Creature|world|etc. <- Game

sentient_races = []
NATURE_FORCE = 'Nature'
CHAOS_FORCE = 'Chaos'
ORDER_FORCE = 'Order'
force_colors = {NATURE_FORCE: config.nature_color,
                CHAOS_FORCE: config.chaos_color,
                ORDER_FORCE: config.order_color}
COLD_CLIMATE = 'Cold'
TEMPERATE_CLIMATE = 'Temperate'
HOT_CLIMATE = 'Hot'
ALL_CLIMATES = [COLD_CLIMATE, HOT_CLIMATE, TEMPERATE_CLIMATE]


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


class Helmet(Item):
    pass


class Armor(Item):
    pass


class Back(Item):
    pass


class Boots(Item):
    pass


class MainHand(Item):
    pass


class Offhand(Item):
    pass


class Teeth(Item):
    pass


class Hide(Item):
    pass


class Claws(Item):
    pass


class Tail(Item):
    pass


class Meat(Item):
    pass


base_sentient_equipment_slots = {'Head': Helmet, 'Armor': Armor, 'Back': Back,
                                 'Boots': Boots, 'Main hand': MainHand, 'Offhand': Offhand}
base_animal_equipment_slots = {'Teeth': Teeth, 'Hide': Hide, 'Claws': Claws, 'Tail': Tail, 'Meat': Meat}


class Species(GameObject):
    _equipment_slots = {}

    @property
    def base_stats(self) -> dict[str, int]:
        raise NotImplementedError(f'Class {self.__class__} must implement base stats!')

    @property
    def equipment_slots(self):
        return self._equipment_slots


class SentientSpecies(Species):
    @property
    def base_stats(self) -> dict[str, int]:
        return {'Str': 5, 'End': 5, 'Will': 5, 'Dex': 5}

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        sentient_races.append(self)
        self._equipment_slots = base_sentient_equipment_slots.copy()


class AnimalSpecies(Species):
    @property
    def base_stats(self) -> dict[str, int]:
        return self._base_stats

    def __init__(self, base_stats: dict[str, int] = None, **kwargs):
        super().__init__(**kwargs)
        self._base_stats = base_stats or {'Str': 1, 'End': 1, 'Will': 1, 'Dex': 1}
        self._equipment_slots = base_animal_equipment_slots.copy()


human_race = SentientSpecies(name='Human',
                             icon='H',
                             color=config.order_color,
                             description='Explorers and treasure seekers, the human race combines the primal need '
                                         'of discovery with the perseverance that gave birth to all great empires.',
                             sort_key=0)
dwarf_race = SentientSpecies(name='Dwarf',
                             icon='D',
                             color=config.order_color,
                             description='Masters of the forge, they are drawn down into the depths of the world by '
                                         'an ancient instinct that rivals the bravery of human explorers.',
                             sort_key=1)
gnome_race = SentientSpecies(name='Gnome',
                             icon='G',
                             color=config.order_color,
                             description='The only race that views rocks as living things,'
                                         ' gnomes are friendly and easygoing.',
                             sort_key=2)
elf_race = SentientSpecies(name='Elf',
                           icon='E',
                           color=config.order_color,
                           description='Expert mages and librarians, the elves have given the world'
                                       ' a lot of legendary heroes.',
                           sort_key=3)
orc_race = SentientSpecies(name='Orc',
                           icon='O',
                           color=config.chaos_color,
                           description='The most aggressive of races, orcs crave combat above all else.'
                                       ' They always keep a spare weapon around, just in case.',
                           sort_key=4)
troll_race = SentientSpecies(name='Troll',
                             icon='T',
                             color=config.chaos_color,
                             description="Finding a tasty rock to eat makes a troll's day. Having "
                                         "someone to throw a rock at is a bonus that only a troll "
                                         "can appreciate in full.",
                             sort_key=5)
goblin_race = SentientSpecies(name='Goblin',
                              icon='G',
                              color=config.chaos_color,
                              description="For a goblin, everything can come in handy one day. They are"
                                          " legendary pilferers and pillagers, and leave no one, and nothing, behind.",
                              sort_key=6)
kraken_race = SentientSpecies(name='Kraken',
                              icon='K',
                              color=config.chaos_color,
                              description="Descendants of deep sea monsters, the kraken have learned to "
                                          "reap even the most disgusting of water dwellers for useful substances.",
                              sort_key=7)
imp_race = SentientSpecies(name='Imp',
                           icon='I',
                           color=config.chaos_color,
                           description="Fire burns in an imp's veins and dances over their fingers."
                                       " To burn is to feel alive!",
                           sort_key=8)
dryad_race = SentientSpecies(name='Dryad',
                             icon='D',
                             color=config.nature_color,
                             description="The kin of plants, dryads are champions of the forest. They give"
                                         " trees their all and received undying love in return.",
                             sort_key=9)
shifter_race = SentientSpecies(name='Shifter',
                               icon='S',
                               color=config.nature_color,
                               description="A shifter can easily pass as a human if they cut their talon-like nails "
                                           "and keep their totemic tattoos hidden. They rarely do.",
                               sort_key=10)
water_elemental_race = SentientSpecies(name='Water Elemental',
                                       icon='W',
                                       color=config.nature_color,
                                       description="To make other living beings see the beauty of water, elementals "
                                                   "turn it into art, home, and sustenance.",
                                       sort_key=11)
fay_race = SentientSpecies(name='Fay',
                           icon='F',
                           color=config.nature_color,
                           description="The fay are born from the natural magic of the world, and "
                                       "they have developed methods to manipulate it. Their ability to "
                                       "trespass into the dreams of others is an insignificant side effect.",
                           sort_key=12)
fox_species = AnimalSpecies(name='Fox', icon='f', color=console.fg.lightred)


class Creature(GameObject):
    # TODO: Creatures have goals and they ask the Location for the path to the closest
    #  Tile that satisfies the goal
    def __init__(self, race: Species = None, **kwargs):
        super().__init__(**kwargs)
        self.race = race
        self.stats = self.race.base_stats.copy()
        self.equipment_slots = self.race.equipment_slots
        self.current_equipment = {k: None for k in self.equipment_slots}
        # TODO: Add ageing for NPCs here between the stats and the sub-stats
        self.hp = self.max_hp
        self.mana = self.max_mana
        self.energy = self.max_energy
        self.load = 0

    @property
    def max_hp(self):
        return self.stats['Str'] + 2 * self.stats['End']

    @property
    def max_mana(self):
        return self.stats['Will'] * 10

    @property
    def max_energy(self):
        return self.stats['End'] * 10

    @property
    def max_load(self):
        return self.stats['Str'] * 5


class Fox(Creature):
    def __init__(self):
        super().__init__(race=fox_species, name='fox', icon='f', color=console.fg.lightred)


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
    equipment_substate = 'equipment_screen'
    equip_for_substate = 'equip_for_screen'
    high_score_state = 'high_score'
    ended_state = 'ended'
    races = sentient_races

    def __init__(self):
        self.character: Optional[Creature] = None
        self._current_location: Optional[Location] = None
        self.character_name: Optional[str] = None
        self._equipping_for: Optional[str] = None
        self._creature_coords: dict[tuple[int, int], Creature] = {}
        self.world: Optional[World] = None
        self.state: str = Game.welcome_state
        self.substate: Optional[str] = None

    def start_game(self, character_race) -> None:
        if character_race is None:
            return
        self.character = Creature(name=self.character_name, race=character_race,
                                  description='You are standing here.', color=console.fg.default,
                                  icon='@')
        initial_coords = (0, 0)
        self._creature_coords[initial_coords] = self.character
        self._current_location = self.world.get_location(initial_coords)
        self._creature_coords = self._current_location.load_creatures(self._creature_coords)
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
        if self.state is Game.welcome_state:
            return {commands.NewGame(): self._new_game,
                    commands.LoadGame(): self._initiate_load}
        elif self.state is Game.playing_state and self.substate is Game.scene_substate:
            return {commands.Move(): self._move_character,
                    commands.Map(): self._open_map,
                    commands.Equipment(): self._open_equipment}
        elif self.state is Game.playing_state and self.substate is Game.map_substate:
            return {commands.Close(): self._back_to_scene}
        else:
            return {}

    def _open_equipment(self, _) -> bool:
        self.substate = Game.equipment_substate
        return True

    def _back_to_scene(self, _) -> bool:
        self.substate = Game.scene_substate
        return True

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

    def _get_coords_of_creature(self, creature: Creature) -> tuple[int, int]:
        for coords in self._creature_coords:
            if self._creature_coords[coords] is creature:
                return coords
        raise ValueError(f'Creature {creature.name} cannot be found in coords dictionary!')

    def get_equipment_data(self) -> dict[str, Item]:
        return self.character.current_equipment

    def get_available_equipment(self) -> list[GameObject]:
        return []

    def equip_item(self, item):
        if item is not None:
            self.character.current_equipment[self._equipping_for] = item
        self.substate = Game.equipment_substate
        self._equipping_for = None

    def equip_for(self, slot: str):
        self._equipping_for = slot
        if self._equipping_for is None:
            self.substate = Game.scene_substate
        else:
            self.substate = Game.equip_for_substate

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
        return self._current_location.data_with_creatures(self._creature_coords)

    def get_character_position_in_location(self) -> tuple[int, int]:
        return self._get_coords_of_creature(self.character)[0] % config.location_height, \
               self._get_coords_of_creature(self.character)[1] % config.location_width

    def get_world_data(self) -> str:
        return self.world.data()

    def get_region_data(self, coords: tuple[int, int] = None) -> str:
        if coords is None:
            coords = self._get_coords_of_creature(self.character)
        return self.world.get_region_data(coords)

    def _move_creature(self, creature: Creature, direction: str) -> None:
        # TODO: Once the character moves to a new location,
        #     the Game sends the old Location to the World for saving and requests a new one.
        creature_location = self.world.get_location(self._get_coords_of_creature(creature))
        if creature_location is not self._current_location:
            raise ValueError(f'Creatures outside of current location should not be moving! '
                             f'{creature.name} {self._get_coords_of_creature(creature)}')
        new_coords = self._calculate_new_position(self._get_coords_of_creature(creature), direction)
        old_location = self._current_location
        new_location = self.world.get_location(new_coords)
        if new_location.can_ocupy(creature, new_coords) and new_coords not in self._creature_coords:
            self._creature_coords.pop(self._get_coords_of_creature(creature))
            self._creature_coords[new_coords] = creature
            self._current_location = new_location
            if self._current_location is not old_location:
                for coords in list(self._creature_coords.keys()):
                    if self._creature_coords[coords] is not self.character:
                        self._creature_coords.pop(coords)
                self._creature_coords = self._current_location.load_creatures(self._creature_coords)
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
    instances = []

    def __init__(self, passable: bool = True, exhaustion_factor: int = 0,
                 spawned_creatures: tuple[Creature] = (Fox,), **kwargs):
        super().__init__(**kwargs)
        self.passable = passable
        self.exhaustion_factor = exhaustion_factor
        self.spawned_creatures: tuple[Creature] = spawned_creatures
        Terrain.instances.append(self)

    def is_passable_for(self, creature):
        return self.passable


class FlavorTerrain(Terrain):
    def __init__(self, required_base_terrains: list[Terrain] = None,
                 required_climates: list[str] = None, **kwargs):
        super().__init__(**kwargs)
        if required_climates is None or required_base_terrains is None:
            raise ValueError(f'Flavor terrain {self.name} cannot be instantiated without a '
                             f'climate and a required bases list.')
        self._required_base_terrains = required_base_terrains
        self._required_climates = required_climates

    def appears_in(self, base_terrain: Terrain, climate: str):
        return base_terrain in self._required_base_terrains and climate in self._required_climates


# Ground fillers
grass = Terrain(color=console.fg.lightgreen, description='grass')
ashes = Terrain(color=console.fg.lightblack, description='ashes')
dirt = Terrain(color=config.brown_fg_color, description='dirt')
snow = Terrain(color=console.fg.white, description='snow')
sand = Terrain(color=console.fg.yellow, description='sand')
ice = Terrain(color=console.fg.lightblue, description='ice')
# Other base terrains
tree = Terrain(color=console.fg.lightgreen, description='tree', icon='T')
dead_tree = Terrain(color=console.fg.lightblack, description='dead tree', icon='T')
frozen_tree = Terrain(color=console.fg.lightblue, description='frozen tree', icon='T')
ice_block = Terrain(color=console.fg.lightblue, description='ice block', icon='%', passable=False)
rocks = Terrain(color=console.fg.lightblack, description='rocks', icon='%', passable=False)
bush = Terrain(color=console.fg.lightgreen, description='bush', icon='#')
swamp = Terrain(color=console.fg.lightgreen, description='swamp', icon='~')
quick_sand = Terrain(color=console.fg.yellow, description='quicksand')
jungle = Terrain(color=console.fg.green, description='tree', icon='T', passable=False)
all_base_terrains = [grass, ashes, dirt, snow, sand, ice, tree, dead_tree, frozen_tree, ice_block,
                     rocks, bush, swamp, quick_sand, jungle]
# Flavor terrains
poisonous_flowers = FlavorTerrain(color=console.fg.purple, description='poisonous flowers', icon='*',
                                  required_base_terrains=all_base_terrains, required_climates=ALL_CLIMATES)
bones = FlavorTerrain(color=console.fg.lightwhite, description='bones', icon='~',
                      required_base_terrains=all_base_terrains, required_climates=ALL_CLIMATES)
venomous_thorns = FlavorTerrain(color=console.fg.lightgreen, description='venomous thorns', icon='#',
                                required_base_terrains=all_base_terrains, required_climates=ALL_CLIMATES)
junk_pile = FlavorTerrain(color=console.fg.lightblack, description='junk pile', icon='o',
                          required_base_terrains=all_base_terrains, required_climates=ALL_CLIMATES)
lava = FlavorTerrain(color=console.fg.red, description='lava', icon='~', passable=False,
                     required_base_terrains=all_base_terrains, required_climates=[HOT_CLIMATE])
gold_vein = FlavorTerrain(color=console.fg.lightyellow, description='gold vein', icon='%', passable=False,
                          required_base_terrains=[rocks], required_climates=ALL_CLIMATES)
silver_vein = FlavorTerrain(color=console.fg.lightcyan, description='silver vein', icon='%', passable=False,
                            required_base_terrains=[rocks], required_climates=ALL_CLIMATES)
iron_vein = FlavorTerrain(color=console.fg.lightblue, description='iron vein', icon='%', passable=False,
                          required_base_terrains=[rocks], required_climates=ALL_CLIMATES)
mossy_rock = FlavorTerrain(color=console.fg.lightgreen, description='mossy rock', icon='%', passable=False,
                           required_base_terrains=all_base_terrains, required_climates=ALL_CLIMATES)
lichen_clump = FlavorTerrain(color=console.fg.lightgreen, description='lichen clump', icon='o',
                             required_base_terrains=all_base_terrains, required_climates=[COLD_CLIMATE])
flowers = FlavorTerrain(color=console.fg.purple, description='flowers', icon='*',
                        required_base_terrains=all_base_terrains, required_climates=ALL_CLIMATES)
old_pavement = FlavorTerrain(color=console.fg.lightyellow, description='old pavement',
                             required_base_terrains=all_base_terrains, required_climates=ALL_CLIMATES)
ruined_wall = FlavorTerrain(color=config.brown_fg_color, description='ruined wall', icon='#', passable=False,
                            required_base_terrains=all_base_terrains, required_climates=ALL_CLIMATES)
engraved_column = FlavorTerrain(color=config.brown_fg_color, description='engraved column', icon='|', passable=False,
                                required_base_terrains=all_base_terrains, required_climates=ALL_CLIMATES)
fireplace = FlavorTerrain(color=console.fg.lightyellow, description='fireplace', icon='o', passable=False,
                          required_base_terrains=all_base_terrains, required_climates=ALL_CLIMATES)
farmland = FlavorTerrain(color=console.fg.black + config.brown_bg_color, description='farmland', icon='|',
                         required_base_terrains=[grass, dirt, tree, jungle, bush, swamp],
                         required_climates=ALL_CLIMATES)
# Structure building blocks
poisoned_water = Terrain(color=console.fg.lightblack, description='poisoned water', icon='~')
water = Terrain(color=console.fg.blue, description='water', icon='~')
well_terrain = Terrain(color=console.fg.blue, icon='o', name='well', description='a well')


class Well(FlavorTerrain):
    size = (3, 3)
    _data = {}

    def new(self, size: tuple[int, int], filler: Terrain) -> dict[tuple[int, int], Terrain]:
        self._data = {}
        top_left = (random.randint(0, size[0] - self.size[0]),
                    random.randint(0, size[1] - self.size[1]))
        self._add_rectangle(filler=filler, size=self.size, border_only=True, at_coords=top_left)
        self._data[(top_left[0] + 1, top_left[1] + 1)] = well_terrain
        return self._data

    def _add_rectangle(self, filler: Terrain, size: tuple[int, int], border_only: bool = False,
                       at_coords: tuple[int, int] = (0, 0)) -> None:
        for row in range(size[0]):
            for column in range(size[1]):
                if border_only and row not in (0, size[0] - 1) and column not in (0, size[1] - 1):
                    continue
                coords = (at_coords[0] + row, at_coords[1] + column)
                self._data[coords] = filler


well = Well(color=console.fg.blue, description='a well', icon='o',
            required_base_terrains=all_base_terrains,
            required_climates=ALL_CLIMATES)

base_force_terrains = {
    COLD_CLIMATE: {NATURE_FORCE: [snow, rocks, tree],
                   CHAOS_FORCE: [ice, rocks, ice_block],
                   ORDER_FORCE: [snow, frozen_tree, rocks]},
    TEMPERATE_CLIMATE: {NATURE_FORCE: [grass, tree, bush, rocks],
                        CHAOS_FORCE: [ashes, dead_tree, swamp, rocks],
                        ORDER_FORCE: [dirt, tree, bush, rocks]},
    HOT_CLIMATE: {NATURE_FORCE: [sand, rocks, jungle],
                  CHAOS_FORCE: [sand, rocks, quick_sand],
                  ORDER_FORCE: [sand, rocks, bush]}}
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
    COLD_CLIMATE: {NATURE_FORCE: [flowers, mossy_rock, lichen_clump, gold_vein, iron_vein, silver_vein],
                   CHAOS_FORCE: [bones, junk_pile, poisonous_flowers, venomous_thorns],
                   ORDER_FORCE: [ruined_wall, old_pavement, engraved_column, farmland, fireplace]},
    TEMPERATE_CLIMATE: {NATURE_FORCE: [flowers, mossy_rock, gold_vein, iron_vein, silver_vein],
                        CHAOS_FORCE: [bones, junk_pile, poisonous_flowers, venomous_thorns],
                        ORDER_FORCE: [ruined_wall, old_pavement, engraved_column, farmland, fireplace]},
    HOT_CLIMATE: {NATURE_FORCE: [flowers, mossy_rock, gold_vein, iron_vein, silver_vein],
                  CHAOS_FORCE: [bones, junk_pile, poisonous_flowers, venomous_thorns, lava],
                  ORDER_FORCE: [ruined_wall, old_pavement, engraved_column, farmland, fireplace]}}
structures = {
    COLD_CLIMATE: {NATURE_FORCE: [],
                   CHAOS_FORCE: [],
                   ORDER_FORCE: [well]},
    TEMPERATE_CLIMATE: {NATURE_FORCE: [],
                        CHAOS_FORCE: [],
                        ORDER_FORCE: [well]},
    HOT_CLIMATE: {NATURE_FORCE: [],
                  CHAOS_FORCE: [],
                  ORDER_FORCE: [well]}}


class Tile(Container):
    def __init__(self, terrain: Terrain):
        super().__init__(height=3, width=3)
        self.terrain = terrain

    @property
    def contents(self) -> list[list[Item]]:
        self._data_prep()
        return self._contents

    @property
    def description(self):
        return self.terrain.description

    @property
    def icon(self):
        return self.terrain.icon

    def is_passable_for(self, creature: Creature):
        return self.terrain.is_passable_for(creature)


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
        self._climate = climate
        self._terrains: list[Terrain] = []
        self._terrain_weights: list[float] = []
        self._region_name = region_name
        self._filler_terrain = filler_terrains[climate][self._main_force()]
        self._main_terrain = main_terrain
        self._flavor: Optional[FlavorTerrain] = None
        self._flavor_force: Optional[str] = None
        self._structure: Optional[FlavorTerrain] = None
        self._structure_terrains = {}
        self._select_terrains()
        visual = self._structure or self._flavor or main_terrain
        # TODO: Add the structure name
        name = f'{str(self._top_left)}, {self._region_name}'
        super().__init__(height=config.location_height, width=config.location_width,
                         icon=visual.raw_icon, color=visual.color, name=name)

    def load_creatures(self, local_creatures: dict[tuple[int, int], Creature]) -> dict[tuple[int, int], Creature]:
        # TODO: Get random creatures from the filler/base/flavor
        # TODO: Get respawning creatures from the flavor/structure
        # TODO: Get non-respawning creatures from the structure
        creature_lists = [t.spawned_creatures for t in self._terrains]
        weights = self._terrain_weights[:]
        weights[1] += self._forces[self._main_force()]
        weights[2] += self._forces[self._flavor_force]
        for creature_count in range(int(sum(weights) // 20)):
            chosen_list = random.choices(creature_lists, weights=weights)[0]
            chosen_weights = self._generate_weights(len(chosen_list))
            chosen_creature_type = random.choices(chosen_list, chosen_weights)[0]
            new_coords = self._random_coords()
            creature_instance = chosen_creature_type()
            while new_coords in local_creatures or not self.can_ocupy(creature_instance, new_coords):
                new_coords = self._random_coords()
            local_creatures[new_coords] = creature_instance
        return local_creatures

    def _random_coords(self):
        return random.randint(self._top_left[0], self._top_left[0] + self._height - 1), \
            random.randint(self._top_left[1], self._top_left[1] + self._width - 1)

    @staticmethod
    def _generate_weights(list_length):
        return [1 / x for x in range(1, list_length + 1)]

    def _main_force(self) -> str:
        rev_forces = {v: k for k, v in self._forces.items()}
        return rev_forces[max(rev_forces)]

    def _select_terrains(self) -> None:
        max_base_terrain = 40
        max_flavor_terrain = 3
        base_weight = max_base_terrain * self._forces[self._main_force()] / 100
        # Add a flavor terrain
        forces = list(self._forces.keys())
        force_weights = [self._forces[f] for f in forces]
        random_force = random.choices(forces, weights=force_weights)[0]
        available_flavors = [fl for fl in flavor_terrains[self._climate][random_force]
                             if fl.appears_in(self._main_terrain, self._climate)]
        if random.random() > 0.8 and available_flavors:
            flavor = random.choice(available_flavors)
            self._flavor = flavor
            self._flavor_force = random_force
        else:
            flavor = self._main_terrain
            self._flavor_force = self._main_force()
        flavor_weight = max_flavor_terrain * self._forces[random_force] / 100
        # Add filler terrain based on climate & force
        filler_weight = 100 - base_weight - flavor_weight
        self._terrains = [self._filler_terrain, self._main_terrain, flavor]
        self._terrain_weights = [filler_weight, base_weight, flavor_weight]
        # Add a structure
        force = random.choices(forces, weights=force_weights)[0]
        available_structures = [structure for structure in structures[self._climate][force]
                                if structure.appears_in(self._main_terrain, self._climate)]
        if random.random() > 0.9 and available_structures:
            self._structure = random.choice(available_structures)
            self._structure_terrains = self._structure.new((config.location_height, config.location_width),
                                                           self._filler_terrain)

    def _data_prep(self) -> None:
        if not self._contents:
            for row_index in range(self._height):
                row = []
                for column_index in range(self._width):
                    terrain = self._structure_terrains.get((row_index, column_index),
                                                           random.choices(self._terrains,
                                                                          weights=self._terrain_weights)[0])
                    row.append(Tile(terrain=terrain))
                self._contents.append(row[:])

    @property
    def contents(self) -> list[list[Tile]]:
        self._data_prep()
        return self._contents

    def can_ocupy(self, creature: Creature, coords: tuple[int, int]) -> bool:
        return self._tile_at(coords).is_passable_for(creature)

    def _tile_at(self, coords: tuple[int, int]) -> Tile:
        new_coords = self._local_coords(coords)
        try:
            return self.contents[new_coords[0]][new_coords[1]]
        except IndexError:
            raise IndexError(f'Bad coordinates {coords} / {new_coords} for Location tile!')

    def _local_coords(self, coords: tuple[int, int]) -> tuple[int, int]:
        return coords[0] - self._top_left[0], coords[1] - self._top_left[1]

    def data_with_creatures(self, creatures: dict[tuple[int, int], Creature] = None) -> str:
        rows = [[c.icon for c in row]
                for row in self.contents]
        for coords, creature in creatures.items():
            local_coords = self._local_coords(coords)
            rows[local_coords[0]][local_coords[1]] = creature.icon
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
                                   ice_block: 'Ice mountains',
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
                                  jungle: 'Jungles',
                                  quick_sand: 'Desert',
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
