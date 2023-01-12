from typing import Optional, Type
import random
import commands
import console
import config
from utils import calculate_new_position, coord_distance, direct_path

# TODO: Split the objects in modules by level of abstraction:
#  GameObject/Container <- HumanoidSpecies|Item|Creature|world|etc. <- Game

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
climate_colors = {COLD_CLIMATE: console.fg.lightblue,
                  TEMPERATE_CLIMATE: console.fg.lightgreen,
                  HOT_CLIMATE: console.fg.lightred}


class GameObject:
    def __init__(self, name=None, icon='.', color=console.fg.black,
                 description='(empty)', sort_key=0):
        self._name = name
        self.raw_icon = icon
        self.color = color
        self._description = description or name
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

    @property
    def blinking_icon(self):
        return console.fx.blink + self.color + self.raw_icon + console.fx.end

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
        self._contents: list[list] = [[] for _ in range(self._height)]

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

    def data(self, blink_at: tuple[int, int] = None) -> str:
        rows = [[c.icon for c in row]
                for row in self.contents]
        if blink_at is not None:
            rows[blink_at[0]][blink_at[1]] = self.contents[blink_at[0]][blink_at[1]].blinking_icon
        rows = [''.join(row) for row in rows]
        return '\n'.join(rows)

    @property
    def size(self) -> tuple[int, int]:
        return self._height, self._width

    @property
    def item_list(self):
        full_list = []
        for line in self._contents:
            full_list += line
        return full_list


class Item(GameObject):
    def __init__(self, weight: int = 0, **kwargs):
        super().__init__(**kwargs)
        self._own_weight = weight

    def details(self, weight_color=console.fg.default) -> list[str]:
        return [self.name, weight_color + f'Weight: {self._own_weight}' + console.fx.end]

    @property
    def weight(self):
        return self._own_weight


empty_space = Item(icon='.', color=console.fg.lightblack, name='(empty)')


class PhysicalContainer(Container, Item):
    @property
    def weight(self):
        return self._own_weight + sum(item.weight for item in self.item_list)

    @property
    def contents(self) -> list[list[Item]]:
        self._data_prep()
        padded_contents = [row[:] for row in self._contents]
        for row in padded_contents:
            row += [empty_space] * (self._width - len(row))
        return padded_contents

    def add_item(self, item: Item):
        if item is empty_space:
            raise TypeError(f"Cannot add empty_space to container!")
        for row_index in range(self._height):
            if len(self._contents[row_index]) < self._width:
                self._contents[row_index].append(item)
                break

    def remove_item(self, item: Item):
        if item is empty_space:
            raise TypeError(f"Cannot remove empty_space from container!")
        for row in self._contents:
            if item in row:
                row.remove(item)
                break

    def has_space(self) -> bool:
        return len(self.item_list) < self._height * self._width


class Helmet(Item):
    pass


class Armor(Item):
    pass


class HideArmor(Armor):
    def __init__(self):
        super().__init__(name='hide armor', weight=5, icon='(', color=config.brown_fg_color,
                         description='Armor made from light hide')
        self.armor = 1


class LeatherArmor(Armor):
    def __init__(self):
        super().__init__(name='leather armor', weight=6, icon='(', color=config.brown_fg_color,
                         description='Armor made from leather')
        self.armor = 3


class PlateArmor(Armor):
    def __init__(self):
        super().__init__(name='plate armor', weight=15, icon='[', color=console.fg.default,
                         description='Armor made from metal plates')
        self.armor = 5


class Back(PhysicalContainer):
    """Includes cloaks and backpacks"""
    pass


class Bag(Back):
    def __init__(self):
        super().__init__(name='bag', weight=1, width=3, height=1, icon='=',
                         color=console.fg.default, description='A very small bag')


class Boots(Item):
    pass


class MainHand(Item):
    pass


class ShortSword(MainHand):
    def __init__(self, color=console.fg.default):
        super().__init__(name='short sword', weight=3, icon='|', color=color,
                         description='Made for stabbing')
        self.damage = 3


class Offhand(Item):
    pass


class Teeth(Item):
    pass


class CarnivoreSmallTeeth(Teeth):
    def __init__(self):
        super().__init__(name='teeth', weight=1, icon=',', color=console.fg.default,
                         description='The teeth of a small carnivore')
        self.damage = 1


class CarnivoreMediumTeeth(Teeth):
    def __init__(self):
        super().__init__(name='teeth', weight=1, icon=',', color=console.fg.default,
                         description='The teeth of a carnivore')
        self.damage = 3


class Hide(Item):
    pass


class LightHide(Hide):
    def __init__(self):
        super().__init__(name='light hide', weight=5, icon='(', color=config.brown_fg_color,
                         description='The light hide of an animal')
        self.armor = 1


class Claws(Item):
    pass


class Tail(Item):
    pass


class Meat(Item):
    def __init__(self):
        super().__init__(name='meat', weight=1, icon=',', color=console.fg.red,
                         description='The meat of an animal')


base_sentient_equipment_slots = {'Head': Helmet, 'Armor': Armor, 'Back': Back,
                                 'Boots': Boots, 'Main hand': MainHand, 'Offhand': Offhand}
base_animal_equipment_slots = {'Teeth': Teeth, 'Hide': Hide, 'Claws': Claws, 'Tail': Tail, 'Meat': Meat}


# The species define what a creature is physically and how it looks in the game
# This also includes the "equipment" of animal species which is part of the body
class Species(GameObject):
    _equipment_slots = {}
    initial_equipment = ()

    @property
    def base_stats(self) -> dict[str, int]:
        raise NotImplementedError(f'Class {self.__class__} must implement base stats!')

    @property
    def equipment_slots(self):
        return self._equipment_slots


class HumanoidSpecies(Species):
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

    def __init__(self, base_stats: dict[str, int] = None, equipment: list[Type[Item]] = (), **kwargs):
        super().__init__(**kwargs)
        self.initial_equipment = equipment + [Meat]
        self._base_stats = base_stats or {'Str': 1, 'End': 1, 'Will': 1, 'Dex': 1}
        self._equipment_slots = base_animal_equipment_slots.copy()


human_race = HumanoidSpecies(name='Human',
                             icon='H',
                             color=config.order_color,
                             description='Explorers and treasure seekers, the human race combines the primal need '
                                         'of discovery with the perseverance that gave birth to all great empires.',
                             sort_key=0)
dwarf_race = HumanoidSpecies(name='Dwarf',
                             icon='D',
                             color=config.order_color,
                             description='Masters of the forge, they are drawn down into the depths of the world by '
                                         'an ancient instinct that rivals the bravery of human explorers.',
                             sort_key=1)
gnome_race = HumanoidSpecies(name='Gnome',
                             icon='G',
                             color=config.order_color,
                             description='The only race that views rocks as living things,'
                                         ' gnomes are friendly and easygoing.',
                             sort_key=2)
elf_race = HumanoidSpecies(name='Elf',
                           icon='E',
                           color=config.order_color,
                           description='Expert mages and librarians, the elves have given the world'
                                       ' a lot of legendary heroes.',
                           sort_key=3)
orc_race = HumanoidSpecies(name='Orc',
                           icon='O',
                           color=config.chaos_color,
                           description='The most aggressive of races, orcs crave combat above all else.'
                                       ' They always keep a spare weapon around, just in case.',
                           sort_key=4)
troll_race = HumanoidSpecies(name='Troll',
                             icon='T',
                             color=config.chaos_color,
                             description="Finding a tasty rock to eat makes a troll's day. Having "
                                         "someone to throw a rock at is a bonus that only a troll "
                                         "can appreciate in full.",
                             sort_key=5)
goblin_race = HumanoidSpecies(name='Goblin',
                              icon='G',
                              color=config.chaos_color,
                              description="For a goblin, everything can come in handy one day. They are"
                                          " legendary pilferers and pillagers, and leave no one, and nothing, behind.",
                              sort_key=6)
kraken_race = HumanoidSpecies(name='Kraken',
                              icon='K',
                              color=config.chaos_color,
                              description="Descendants of deep sea monsters, the kraken have learned to "
                                          "reap even the most disgusting of water dwellers for useful substances.",
                              sort_key=7)
imp_race = HumanoidSpecies(name='Imp',
                           icon='I',
                           color=config.chaos_color,
                           description="Fire burns in an imp's veins and dances over their fingers."
                                       " To burn is to feel alive!",
                           sort_key=8)
dryad_race = HumanoidSpecies(name='Dryad',
                             icon='D',
                             color=config.nature_color,
                             description="The kin of plants, dryads are champions of the forest. They give"
                                         " trees their all and received undying love in return.",
                             sort_key=9)
shifter_race = HumanoidSpecies(name='Shifter',
                               icon='S',
                               color=config.nature_color,
                               description="A shifter can easily pass as a human if they cut their talon-like nails "
                                           "and keep their totemic tattoos hidden. They rarely do.",
                               sort_key=10)
water_elemental_race = HumanoidSpecies(name='Water Elemental',
                                       icon='W',
                                       color=config.nature_color,
                                       description="To make other living beings see the beauty of water, elementals "
                                                   "turn it into art, home, and sustenance.",
                                       sort_key=11)
fay_race = HumanoidSpecies(name='Fay',
                           icon='F',
                           color=config.nature_color,
                           description="The fay are born from the natural magic of the world, and "
                                       "they have developed methods to manipulate it. Their ability to "
                                       "trespass into the dreams of others is an insignificant side effect.",
                           sort_key=12)
fox_species = AnimalSpecies(name='Fox', icon='f', color=console.fg.lightred,
                            equipment=[CarnivoreSmallTeeth, LightHide])
wolf_species = AnimalSpecies(name='Wolf', icon='w', color=console.fg.lightblack,
                             base_stats={'Str': 4, 'End': 4, 'Will': 1, 'Dex': 7},
                             equipment=[CarnivoreMediumTeeth, LightHide])


class Creature(GameObject):
    # TODO: Creatures have goals and they ask the Location for the path to the closest
    #  Tile that satisfies the goal
    def __init__(self, race: Species = None, **kwargs):
        if kwargs.get('icon') is None:
            kwargs['icon'] = race.raw_icon
        if kwargs.get('color') is None:
            kwargs['color'] = race.color
        super().__init__(**kwargs)
        self.race = race
        self._ai = ['random/']
        self.stats = self.race.base_stats.copy()
        self.equipment_slots = self.race.equipment_slots
        self.current_equipment = {k: empty_space for k in self.equipment_slots}
        for item_type in self.race.initial_equipment:
            self.swap_equipment(item_type())
        # TODO: Add ageing for NPCs here between the stats and the sub-stats
        self._hp = self.max_hp
        self._mana = self.max_mana
        self._energy = self.max_energy

    @property
    def load(self):
        return sum([item.weight for item in self.current_equipment.values()])

    @property
    def damage(self) -> int:
        return random.randint(1, max(self.stats['Str'] // 4, 1)) + self.weapon_damage()

    @property
    def armor(self) -> int:
        return random.randint(int(self.equipment_armor() * self.stats['Dex'] / config.max_stat_value),
                              self.equipment_armor())

    def equipment_armor(self) -> int:
        armor = 0
        for item in self.current_equipment.values():
            try:
                armor += item.armor
            except AttributeError:
                pass
        return armor

    def weapon_damage(self) -> int:
        dmg = 0
        for item in self.current_equipment.values():
            try:
                dmg += item.damage
            except AttributeError:
                pass
        return dmg

    @property
    def hp(self):
        return self._hp

    @hp.setter
    def hp(self, value):
        self._hp = min(self.max_hp, value)

    @property
    def energy(self):
        return self._energy

    @energy.setter
    def energy(self, value):
        self._energy = min(self.max_energy, value)

    @property
    def mana(self):
        return self._mana

    @mana.setter
    def mana(self, value):
        self._mana = min(self.max_mana, value)

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

    @property
    def bag(self):
        return self.current_equipment['Back']

    def can_equip(self, item: Item) -> bool:
        return any([isinstance(item, slot_type) for slot_type in self.equipment_slots.values()])

    def can_carry(self, item: Item) -> bool:
        return item.weight <= self.max_load - self.load

    def can_swap_equipment(self, item: Item) -> bool:
        for slot, slot_type in self.equipment_slots.items():
            if isinstance(item, slot_type):
                available_load = self.max_load - self.load
                load_difference = item.weight - self.current_equipment[slot].weight
                return available_load >= load_difference
        return False

    def swap_equipment(self, item: Item) -> Item:
        for slot, slot_type in self.equipment_slots.items():
            if isinstance(item, slot_type):
                old_item = self.current_equipment[slot]
                self.current_equipment[slot] = item
                return old_item

    def get_goals(self) -> list[str]:
        return self._ai

    def get_drops(self):
        return [item for item in self.current_equipment.values() if item is not empty_space]

    def bump_with(self, other_creature: 'Creature') -> None:
        other_creature.receive_damage(self.damage)

    def receive_damage(self, damage: int) -> None:
        load_modifier = (self.max_load - self.load) / self.max_load
        if random.random() > self.stats['Dex'] / config.max_stat_value * load_modifier:
            self.hp -= max(0, damage - self.armor)

    def rest(self):
        self.energy += random.randint(1, max(self.stats['End'] // 5, 1))
        if random.random() < (self.stats['End'] / config.max_stat_value / 2) * (self.energy / self.max_energy):
            self.hp += 1

    @property
    def is_dead(self) -> bool:
        return self.hp <= 0


# These hold the AI, so they are more like roles than species
class Fox(Creature):
    def __init__(self):
        super().__init__(race=fox_species, name='fox')
        self._ai = ['random/']


class Wolf(Creature):
    def __init__(self):
        super().__init__(race=wolf_species, name='wolf')
        self._ai = [f'chase/{self.stats["Dex"]}', 'random/']


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
    inventory_substate = 'inventory_substate'
    high_score_state = 'high_score'
    ended_state = 'ended'
    races = sentient_races

    def __init__(self):
        self._turn = 0
        self.character: Optional[Creature] = None
        self._current_location: Optional[Location] = None
        self.character_name: Optional[str] = None
        self._equipping_slot: Optional[str] = None
        self._equipment_locations: dict[Item, str] = {}
        self._selected_ground_item = empty_space
        self._selected_bag_item = empty_space
        self._active_inventory_container_name = '(none)'
        self._ground_container = None
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
        # TODO: This is the initial testing configuration. Add the selected starting location here.
        initial_coords = (0, 0)
        self._creature_coords[initial_coords] = self.character
        self._current_location = self.world.get_location(initial_coords)
        self._creature_coords = self._current_location.load_creatures(self._creature_coords)
        self._current_location.put_item(Bag(), initial_coords)
        self._current_location.put_item(ShortSword(color=console.fg.red), initial_coords)
        self._current_location.put_item(PlateArmor(), initial_coords)

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
            return {commands.Move(): self._player_move,
                    commands.Rest(): self._character_rests,
                    commands.Map(): self._open_map,
                    commands.Equipment(): self._open_equipment,
                    commands.Inventory(): self._open_inventory}
        elif self.state is Game.playing_state and self.substate is Game.map_substate:
            return {commands.Close(): self._back_to_scene}
        elif self.state is Game.playing_state and self.substate is Game.inventory_substate:
            inventory_commands = {commands.Close(): self._back_to_scene}
            if self.character.bag is not empty_space \
               and self.character.bag.has_space() \
               and self.character.can_carry(self._selected_ground_item) \
               and self._selected_ground_item is not empty_space \
               and self._active_inventory_container_name == self.get_ground_name():
                inventory_commands[commands.InventoryPickUp()] = self._pick_up_item
            if self.character.can_swap_equipment(self._selected_ground_item) \
               and self._selected_ground_item is not empty_space \
               and self._active_inventory_container_name == self.get_ground_name():
                inventory_commands[commands.InventoryEquip()] = self._equip_from_ground_in_inventory_screen
            if self._selected_bag_item is not empty_space \
               and self._ground_container.has_space() \
               and self._active_inventory_container_name == self.get_bag_name():
                inventory_commands[commands.InventoryDrop()] = self._drop_from_inventory_screen
            if self.character.can_equip(self._selected_bag_item) \
               and self._active_inventory_container_name == self.get_bag_name():
                inventory_commands[commands.InventoryEquip()] = self._equip_from_bag_in_inventory_screen
            return inventory_commands
        else:
            return {}

    def _character_rests(self, _) -> bool:
        self.character.rest()
        self._move_world()
        return True

    def _drop_from_inventory_screen(self, _) -> bool:
        self.character.bag.remove_item(self._selected_bag_item)
        self._ground_container.add_item(self._selected_bag_item)
        return True

    def _equip_from_bag_in_inventory_screen(self, _):
        self.character.bag.remove_item(self._selected_bag_item)
        unequipped_item = self.character.swap_equipment(self._selected_bag_item)
        if unequipped_item is not empty_space:
            self.character.bag.add_item(unequipped_item)
        return True

    def _equip_from_ground_in_inventory_screen(self, _):
        self._ground_container.remove_item(self._selected_ground_item)
        dropped_item = self.character.swap_equipment(self._selected_ground_item)
        if dropped_item is not empty_space:
            self._ground_container.add_item(dropped_item)
        return True

    def _pick_up_item(self, _) -> bool:
        self._ground_container.remove_item(self._selected_ground_item)
        self.character.bag.add_item(self._selected_ground_item)
        return True

    def _open_inventory(self, _) -> bool:
        self.substate = Game.inventory_substate
        self._ground_container = self._current_location.tile_at(self._get_coords_of_creature(self.character))
        return True

    def _open_equipment(self, _) -> bool:
        self.substate = Game.equipment_substate
        return True

    def _back_to_scene(self, _) -> bool:
        self.substate = Game.scene_substate
        return True

    def _open_map(self, _) -> bool:
        self.substate = Game.map_substate
        return True

    def _player_move(self, direction):
        self._move_character(direction)
        self._move_world()
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

    def _move_world(self):
        # TODO: Change effect visuals (blinking fires, etc)
        self._turn += 1
        self._move_npcs()

    def _move_npcs(self):
        for old_coords in list(self._creature_coords.keys()):
            creature = self._creature_coords.get(old_coords)
            if creature is self.character or creature is None:
                continue
            goals = creature.get_goals()
            next_coords = self._current_location.get_goal_step(creature, old_coords,
                                                               goals, self._creature_coords)
            if next_coords in self._creature_coords:
                other_creature = self._creature_coords[next_coords]
                creature.bump_with(other_creature)
                if other_creature.is_dead:
                    for item in other_creature.get_drops():
                        self._current_location.put_item(item, next_coords)
                    self._creature_coords.pop(next_coords)
            else:
                self._creature_coords.pop(old_coords)
                self._creature_coords[next_coords] = creature

    def _get_coords_of_creature(self, creature: Creature) -> tuple[int, int]:
        for coords in self._creature_coords:
            if self._creature_coords[coords] is creature:
                return coords
        raise ValueError(f'Creature {creature.name} cannot be found in coords dictionary!')

    def get_equipment_data(self) -> dict[str, Item]:
        return self.character.current_equipment

    def get_available_equipment(self) -> list[GameObject]:
        tile_items = self._current_location.items_at(self._get_coords_of_creature(self.character))
        if self._equipping_slot is None:
            raise ValueError(f'Game _equipping_slot cannot be None while searching for equipment!')
        else:
            item_type = self.character.equipment_slots[self._equipping_slot]
        filtered_items = [item for item in tile_items if isinstance(item, item_type)]
        for item in filtered_items:
            self._equipment_locations[item] = 'tile'
        return filtered_items

    def equip_item_from_ground(self, item):
        if item is not None:
            self.character.current_equipment[self._equipping_slot] = item
            self._current_location.remove_item(item, self._get_coords_of_creature(self.character))
        self.substate = Game.equipment_substate
        self._equipping_slot = None

    def equip_for(self, slot: str):
        self._equipping_slot = slot
        if self._equipping_slot is None:
            self.substate = Game.scene_substate
        else:
            if self.character.current_equipment[self._equipping_slot] is not empty_space:
                self.character.current_equipment[self._equipping_slot] = empty_space
                self._equipping_slot = None
            else:
                self.substate = Game.equip_for_substate

    def set_active_container(self, container_name: str) -> None:
        self._active_inventory_container_name = container_name

    def get_bag_name(self) -> str:
        return '(no bag)' if self.character.bag is empty_space else f'Your {self.character.bag.name}'

    def get_ground_name(self) -> str:
        return config.ground if not self._ground_container.name else self._ground_container.name

    def get_ground_items(self) -> str:
        return self._current_location.get_items_data_at(self._get_coords_of_creature(self.character))

    def get_bag_items(self) -> str:
        return '' if self.character.bag is empty_space else self.character.bag.data()

    def get_bag_size(self) -> tuple[int, int]:
        return (0, 0) if self.character.bag is empty_space else self.character.bag.size

    def get_ground_item_details(self, item_coords: tuple[int, int]) -> list[str]:
        weight_color = console.fg.default
        self._selected_ground_item = self._ground_container.contents[item_coords[0]][item_coords[1]]
        if not self.character.can_carry(self._selected_ground_item):
            weight_color = console.fg.lightred
        return self._selected_ground_item.details(weight_color=weight_color)

    def get_bag_item_details(self, item_coords: tuple[int, int]) -> list[str]:
        try:
            self._selected_bag_item = self.character.bag.contents[item_coords[0]][item_coords[1]]
        except AttributeError:
            self._selected_bag_item = empty_space
        return self._selected_bag_item.details()

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
        hud = f'HP [{hp_gauge}] | Mana [{mana_gauge}] | Energy [{energy_gauge}] | Load [{load_gauge}]\n'
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

    def get_character_position_in_region(self) -> tuple[int, int]:
        row, column = self._get_coords_of_creature(self.character)
        row = (row % (config.region_size * config.location_height)) // config.location_height
        column = (column % (config.region_size * config.location_width)) // config.location_width
        return row, column

    def get_character_position_in_world(self) -> tuple[int, int]:
        row, column = self._get_coords_of_creature(self.character)
        row = row // (config.region_size * config.location_height)
        column = column // (config.region_size * config.location_width)
        return row, column

    def get_world_data(self, blink_at: tuple[int, int]) -> str:
        return self.world.data(blink_at, character_at=self._get_coords_of_creature(self.character))

    def get_region_data(self, coords: tuple[int, int], blink_at: tuple[int, int]) -> str:
        return (self.world
                .contents[coords[0]][coords[1]]
                .data(blink_at, character_at=self._get_coords_of_creature(self.character)))

    def get_region_map_details(self, coords: tuple[int, int]) -> list[str]:
        return self.world.contents[coords[0]][coords[1]].map_details

    def get_location_map_details(self, region_coords: tuple[int, int],
                                 location_coords: tuple[int, int]) -> list[str]:
        region = self.world.contents[region_coords[0]][region_coords[1]]
        location = region.contents[location_coords[0]][location_coords[1]]
        return location.map_details

    def _move_character(self, direction: str) -> None:
        # TODO: Once the character moves to a new location,
        #     the Game sends the old Location to the World for saving and requests a new one.
        old_coords = self._get_coords_of_creature(self.character)
        new_coords = calculate_new_position(old_coords, direction, *self.world.size)
        old_location = self._current_location
        new_location = self.world.get_location(new_coords)
        if new_location.can_ocupy(self.character, new_coords):
            if new_coords in self._creature_coords:
                other_creature = self._creature_coords[new_coords]
                self.character.bump_with(other_creature)
                if other_creature.is_dead:
                    for item in other_creature.get_drops():
                        self._current_location.put_item(item, new_coords)
                    self._creature_coords.pop(new_coords)
            else:
                self._creature_coords.pop(old_coords)
                self._creature_coords[new_coords] = self.character
                self._current_location = new_location
            if self._current_location is not old_location:
                for coords in list(self._creature_coords.keys()):
                    if self._creature_coords[coords] is not self.character:
                        self._creature_coords.pop(coords)
                self._creature_coords = self._current_location.load_creatures(self._creature_coords)
        else:
            # TODO: Implement log message describing why the move is impossible
            pass


# TODO: Add Terrains
class Terrain(GameObject):
    instances = []

    def __init__(self, passable: bool = True, exhaustion_factor: int = 0,
                 spawned_creatures: tuple[Creature] = (Fox, Wolf), **kwargs):
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
grass = Terrain(color=console.fg.lightgreen, name='grass')
ashes = Terrain(color=console.fg.lightblack, name='ashes')
dirt = Terrain(color=config.brown_fg_color, name='dirt')
snow = Terrain(color=console.fg.white, name='snow')
sand = Terrain(color=console.fg.yellow, name='sand')
ice = Terrain(color=console.fg.lightblue, name='ice')
# Other base terrains
tree = Terrain(color=console.fg.lightgreen, name='tree', icon='T')
dead_tree = Terrain(color=console.fg.lightblack, name='dead tree', icon='T')
frozen_tree = Terrain(color=console.fg.lightblue, name='frozen tree', icon='T')
ice_block = Terrain(color=console.fg.lightblue, name='ice block', icon='%', passable=False)
rocks = Terrain(color=console.fg.lightblack, name='rocks', icon='%', passable=False)
bush = Terrain(color=console.fg.lightgreen, name='bush', icon='#')
swamp = Terrain(color=console.fg.lightgreen, name='swamp', icon='~')
quick_sand = Terrain(color=console.fg.yellow, name='quicksand')
jungle = Terrain(color=console.fg.green, name='tree', icon='T', passable=False)
all_base_terrains = [grass, ashes, dirt, snow, sand, ice, tree, dead_tree, frozen_tree, ice_block,
                     rocks, bush, swamp, quick_sand, jungle]
# Flavor terrains
poisonous_flowers = FlavorTerrain(color=console.fg.purple, name='poisonous flowers', icon='*',
                                  required_base_terrains=all_base_terrains, required_climates=ALL_CLIMATES)
bones = FlavorTerrain(color=console.fg.lightwhite, name='bones', icon='~',
                      required_base_terrains=all_base_terrains, required_climates=ALL_CLIMATES)
venomous_thorns = FlavorTerrain(color=console.fg.lightgreen, name='venomous thorns', icon='#',
                                required_base_terrains=all_base_terrains, required_climates=ALL_CLIMATES)
junk_pile = FlavorTerrain(color=console.fg.lightblack, name='junk pile', icon='o',
                          required_base_terrains=all_base_terrains, required_climates=ALL_CLIMATES)
lava = FlavorTerrain(color=console.fg.red, name='lava', icon='~', passable=False,
                     required_base_terrains=all_base_terrains, required_climates=[HOT_CLIMATE])
gold_vein = FlavorTerrain(color=console.fg.lightyellow, name='gold vein', icon='%', passable=False,
                          required_base_terrains=[rocks], required_climates=ALL_CLIMATES)
silver_vein = FlavorTerrain(color=console.fg.lightcyan, name='silver vein', icon='%', passable=False,
                            required_base_terrains=[rocks], required_climates=ALL_CLIMATES)
iron_vein = FlavorTerrain(color=console.fg.lightblue, name='iron vein', icon='%', passable=False,
                          required_base_terrains=[rocks], required_climates=ALL_CLIMATES)
mossy_rock = FlavorTerrain(color=console.fg.lightgreen, name='mossy rock', icon='%', passable=False,
                           required_base_terrains=all_base_terrains, required_climates=ALL_CLIMATES)
lichen_clump = FlavorTerrain(color=console.fg.lightgreen, name='lichen clump', icon='o',
                             required_base_terrains=all_base_terrains, required_climates=[COLD_CLIMATE])
flowers = FlavorTerrain(color=console.fg.purple, name='flowers', icon='*',
                        required_base_terrains=all_base_terrains, required_climates=ALL_CLIMATES)
old_pavement = FlavorTerrain(color=console.fg.lightyellow, name='old pavement',
                             required_base_terrains=all_base_terrains, required_climates=ALL_CLIMATES)
ruined_wall = FlavorTerrain(color=config.brown_fg_color, name='ruined wall', icon='#', passable=False,
                            required_base_terrains=all_base_terrains, required_climates=ALL_CLIMATES)
engraved_column = FlavorTerrain(color=config.brown_fg_color, name='engraved column', icon='|', passable=False,
                                required_base_terrains=all_base_terrains, required_climates=ALL_CLIMATES)
fireplace = FlavorTerrain(color=console.fg.lightyellow, name='fireplace', icon='o', passable=False,
                          required_base_terrains=all_base_terrains, required_climates=ALL_CLIMATES)
farmland = FlavorTerrain(color=console.fg.green + config.brown_bg_color, name='farmland', icon='=',
                         required_base_terrains=[grass, dirt, tree, jungle, bush, swamp],
                         required_climates=ALL_CLIMATES)
# Structure building blocks
poisoned_water = Terrain(color=console.fg.lightblack, name='poisoned water', icon='~')
water = Terrain(color=console.fg.blue, name='water', icon='~')
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


well = Well(color=console.fg.blue, name='a well', icon='o',
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


class Tile(PhysicalContainer):
    def __init__(self, terrain: Terrain):
        super().__init__(height=config.tile_size, width=config.tile_size)
        self.terrain = terrain

    @property
    def description(self):
        return self.terrain.description

    @property
    def icon(self):
        items = self.item_list
        if len(items) == 1:
            return items[0].icon
        elif len(items) > 1:
            return config.multiple_items_icon
        return self.terrain.icon

    def is_passable_for(self, creature: Creature):
        return self.terrain.is_passable_for(creature)

    def has_space(self):
        return self.terrain.passable and len(self.item_list) < self._height * self._width


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
        self._local_name = None if self._structure is None else self._structure.name
        if self._local_name:
            name = ', '.join([self._local_name, self._region_name])
        else:
            name = self._region_name
        super().__init__(height=config.location_height, width=config.location_width,
                         icon=visual.raw_icon, color=visual.color, name=name)
        self._contents: list[list[Tile]] = []

    def get_goal_step(self, creature: Creature, current_coords: tuple[int, int],
                      goals: list[str], creatures: dict[tuple[int, int], Creature]) -> tuple[int, int]:
        for goal in goals:
            goal_type, param = goal.split('/')
            if goal_type == 'chase':
                step = self._find_prey(current_coords, distance=int(param), creatures=creatures)
                if step == current_coords:
                    continue
                else:
                    return step
            elif goal_type == 'random':
                return self._choose_random_passable_neighbor(creature, current_coords)

    @staticmethod
    def _find_prey(coords, distance: int,
                   creatures: dict[tuple[int, int], Creature]) -> tuple[int, int]:
        for prey_coords, prey in creatures.items():
            if isinstance(prey.race, HumanoidSpecies) and coord_distance(coords, prey_coords) < distance:
                path = direct_path(coords, prey_coords)
                return path[1]
        return coords

    def _all_neighbors(self, coords: tuple[int, int]) -> list[tuple[int, int]]:
        neighbors = []
        for change_x in [-1, 0, 1]:
            for change_y in [-1, 0, 1]:
                new_y = coords[0] + change_y
                new_x = coords[1] + change_x
                if new_x < self._top_left[1] or new_y < self._top_left[0] \
                   or new_x >= self._width + self._top_left[1] \
                   or new_y >= self._height + self._top_left[0] \
                   or (new_y, new_x) == coords:
                    continue
                neighbors.append((new_y, new_x))
        return neighbors

    def _choose_random_passable_neighbor(self, creature: Creature,
                                         coords: tuple[int, int]) -> tuple[int, int]:
        neighbors = self._all_neighbors(coords)
        random.shuffle(neighbors)
        for new_coords in neighbors:
            if self.tile_at(new_coords).is_passable_for(creature):
                return new_coords
        else:
            return coords

    def get_items_data_at(self, coords: tuple[int, int]) -> str:
        return self.tile_at(coords).data()

    def get_item_at(self, character_coords: tuple[int, int], item_coords: tuple[int, int]) -> Item:
        return self.tile_at(character_coords).contents[item_coords[0]][item_coords[1]]

    @property
    def map_details(self) -> list[str]:
        flavor_name = None if self._flavor is None else self._flavor.name
        return [f'Landmark: {self._local_name}', f'Features: {flavor_name}']

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
        return self.tile_at(coords).is_passable_for(creature)

    def tile_at(self, coords: tuple[int, int]) -> Tile:
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

    def items_at(self, coords: tuple[int, int]) -> list[Item]:
        return self.tile_at(coords).item_list

    def put_item(self, item: Item, coords: tuple[int, int]) -> None:
        tile = self.tile_at(coords)
        if tile.has_space():
            tile.add_item(item)
        else:
            raise NotImplementedError(f'Implement flood fill algorithm for getting a tile with enough space.')

    def remove_item(self, item: Item, coords: tuple[int, int]) -> None:
        self.tile_at(coords).remove_item(item)


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
                                  rocks: 'Crag'}}

    def __init__(self, top_left: tuple[int, int], main_force: str, climate: str, suffix: str = ' of tests'):
        self._top_left = top_left
        self._main_force = main_force
        self._climate = climate
        self._main_terrain: Terrain = random.choice(base_force_terrains[self._climate][self._main_force])
        raw_name = f'{Region.region_names[self._climate][self._main_terrain]} {suffix}'
        name = f'{force_colors[self._main_force]}{raw_name}{console.fx.end}'
        super().__init__(height=config.region_size, width=config.region_size,
                         name=name, icon=self._main_terrain.raw_icon, color=self._main_terrain.color)

    @property
    def map_details(self) -> list[str]:
        colored_force = force_colors[self._main_force] + self._main_force + console.fx.end
        colored_climate = climate_colors[self._climate] + self._climate + console.fx.end
        return [f'Region: {self.name}', f'Force: {colored_force}', f'Climate: {colored_climate}']

    def _data_prep(self) -> None:
        if not self._contents[0]:
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

    def _get_location_coords_from_absolute_coords(self, coords: tuple[int, int]) -> tuple[int, int]:
        local_row_in_tiles = coords[0] - self._top_left[0]
        local_column_in_tiles = coords[1] - self._top_left[1]
        location_row = local_row_in_tiles // config.location_height
        location_column = local_column_in_tiles // config.location_width
        return location_row, location_column

    def get_location(self, coords: tuple[int, int]) -> Location:
        row, column = self._get_location_coords_from_absolute_coords(coords)
        return self.contents[row][column]

    def data(self, blink_at: tuple[int, int] = None, character_at: tuple[int, int] = None) -> str:
        rows = [[c.icon for c in row]
                for row in self.contents]
        if blink_at is not None:
            rows[blink_at[0]][blink_at[1]] = self.contents[blink_at[0]][blink_at[1]].blinking_icon
        if character_at is not None:
            character_position = self._get_location_coords_from_absolute_coords(character_at)
            if -1 < character_position[0] < config.region_size \
                    and -1 < character_position[1] < config.region_size:
                rows[character_position[0]][character_position[1]] = '@'
        rows = [''.join(row) for row in rows]
        return '\n'.join(rows)


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

    @staticmethod
    def _get_region_coords_from_absolute_coords(coords: tuple[int, int]) -> tuple[int, int]:
        return coords[0] // Region.height_in_tiles, coords[1] // Region.width_in_tiles

    def get_location(self, coords: tuple[int, int]) -> Location:
        row, column = self._get_region_coords_from_absolute_coords(coords)
        region = self.contents[row][column]
        return region.get_location(coords)

    @property
    def contents(self) -> list[list[Region]]:
        self._data_prep()
        return self._contents

    @property
    def size(self) -> tuple[int, int]:
        return config.world_size * config.region_size * config.location_height, \
               config.world_size * config.region_size * config.location_width

    def data(self, blink_at: tuple[int, int] = None, character_at: tuple[int, int] = None) -> str:
        rows = [[c.icon for c in row]
                for row in self.contents]
        if blink_at is not None:
            rows[blink_at[0]][blink_at[1]] = self.contents[blink_at[0]][blink_at[1]].blinking_icon
        if character_at is not None:
            character_position = self._get_region_coords_from_absolute_coords(character_at)
            rows[character_position[0]][character_position[1]] = '@'
        rows = [''.join(row) for row in rows]
        return '\n'.join(rows)


if __name__ == '__main__':
    bag = PhysicalContainer(1, 1)
    # print(bag._width)
    # print(bag._own_weight)
