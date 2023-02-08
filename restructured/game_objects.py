from typing import Optional, Type, Union
import random
import commands
import console
import config
from utils import calculate_new_position, coord_distance, direct_path, dim, raw_length, make_stats
from knowledge import knowledge

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
                 description=config.empty_string, sort_key=0):
        self._name = name
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

    @property
    def blinking_icon(self):
        return console.fx.blink + self.color + self.raw_icon + console.fx.end

    @staticmethod
    def commands() -> dict:
        return {}

    @staticmethod
    def data() -> str:
        return config.empty_string


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
    def __init__(self, weight: int = 0, effects: dict[str, int] = None,
                 is_stackable: bool = False, **kwargs):
        super().__init__(**kwargs)
        self._own_weight = weight
        self._effects = effects or {}
        self.is_stackable = is_stackable

    def details(self, weight_color=console.fg.default) -> list[str]:
        return [self.name, weight_color + f'Weight: {self.weight}' + console.fx.end]

    @property
    def weight(self):
        return self._own_weight

    @property
    def effects(self) -> dict[str, int]:
        return self._effects


class ItemStack(Item):
    def __init__(self, items: list[Item]):
        unstacked_items = []
        for possible_stack in items:
            if not possible_stack.is_stackable:
                raise TypeError(f"Cannot stack unstackable item {possible_stack.name}!")
            if hasattr(possible_stack, 'items'):
                unstacked_items += possible_stack.items
            else:
                unstacked_items.append(possible_stack)
        if len(set([type(item) for item in unstacked_items])) > 1:
            raise TypeError(f"Cannot stack items of types: {set([type(item) for item in items])}!")
        template = unstacked_items[0]
        super().__init__(effects=template.effects, is_stackable=True,
                         icon=template.raw_icon, color=template.color, description=template.description)
        self.items = unstacked_items

    def __getattr__(self, item):
        return getattr(self.items[0], item)

    @property
    def size(self) -> int:
        return len(self.items)

    @property
    def name(self) -> str:
        if self.size > 1:
            return f'{len(self.items)} {self.items[0].name}s'
        else:
            return self.items[0].name

    @property
    def __class__(self) -> Type:
        return self.items[0].__class__

    @property
    def is_empty(self) -> bool:
        return len(self.items) == 0

    def split(self, count: int) -> Union['ItemStack', Item]:
        if count == 1:
            return self.items.pop()
        if count >= len(self.items):
            count = len(self.items)
        removed_items = self.items[:count]
        self.items = self.items[count:]
        return ItemStack(removed_items)

    @property
    def weight(self) -> int:
        return len(self.items) * self.items[0].weight


class JunkItem(Item):
    def __init__(self):
        name = 'some junk'
        weight = random.randint(1, 4)
        icon = random.choice('*{}()[]|,')
        description = 'an unidentifiable piece of junk'
        color = random.choice([console.fg.purple, console.fg.red, console.fg.yellow, console.fg.blue])
        super().__init__(name=name, weight=weight, icon=icon, description=description, color=color)


empty_space = Item(icon='.', color=console.fg.lightblack, name=config.empty_string)


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

    def add_item(self, item: Item, ignore_stackability: bool = False) -> None:
        if item is self:
            raise ValueError(f"Container {self.name} cannot contain itself!")
        if not self.has_space():
            raise IndexError(f"Container {self.name} has no space for items!")
        if item is empty_space:
            raise TypeError(f"Cannot add empty_space to container {self.name}!")
        if item.is_stackable and not ignore_stackability:
            for possible_stack in self.item_list:
                try:
                    new_stack = ItemStack([possible_stack, item])
                except TypeError:
                    pass
                else:
                    self.remove_item(possible_stack)
                    self.add_item(new_stack, ignore_stackability=True)
                    return
        for row_index in range(self._height):
            if len(self._contents[row_index]) < self._width:
                self._contents[row_index].append(item)
                break

    def remove_item(self, item: Item) -> None:
        if item is empty_space:
            raise TypeError(f"Cannot remove empty_space from container!")
        for row in self._contents:
            if item in row:
                row.remove(item)
                break

    def provide_item(self, max_weight: int, item: Item, max_amount: int = None) -> Item:
        if item not in self.item_list:
            raise ValueError(f"Item {item.name} cannot be found in container {self.name}!")
        if isinstance(item, ItemStack) and item.items[0].weight <= max_weight:
            amount_to_provide = min(max_amount or max_weight // item.items[0].weight,
                                    max_weight // item.items[0].weight)
            item_to_provide = item.split(amount_to_provide)
            if item.is_empty:
                self.remove_item(item)
        elif not isinstance(item, ItemStack) and item.weight <= max_weight:
            item_to_provide = item
            self.remove_item(item)
        else:
            raise ValueError(f"Requested item {item.name} weighs more than the max allowed weight!")
        return item_to_provide

    def has_space(self) -> bool:
        return len(self.item_list) < self._height * self._width


class Liquid(Item):
    """A container class for singleton object instances to be used as liquids in the game"""

    @property
    def name(self) -> str:
        return self.color + self._name + console.fx.end


water_liquid = Liquid(name='water', weight=1, icon=',', color=console.fg.blue,
                      description='The one thing everyone needs',
                      effects={config.thirst_water_effect: 20,
                               config.hunger_water_effect: 0})
wine_liquid = Liquid(name='wine', weight=1, icon=',', color=console.fg.red,
                     description='Fermented fruit juice',
                     effects={config.thirst_water_effect: 15, config.drunk_effect: 10})


class LiquidContainer(Item):
    """An object facilitating interactions with Liquid instances"""

    def __init__(self, max_volume: int = 0, **kwargs):
        super().__init__(**kwargs)
        self._max_volume: int = max_volume
        self.liquid: Optional[Liquid] = None
        self.contained_volume: int = 0
        if '/' not in kwargs.get('name', '') or '{' not in kwargs.get('name', ''):
            raise ValueError("LiquidContainer name must support splitting and formatting!")

    @property
    def name(self) -> str:
        if self.liquid is None:
            return self._name.split('/')[0]
        else:
            return self._name.split('/')[1].format(self.liquid.name)

    @property
    def description(self) -> str:
        if self.liquid is None:
            return f"It can hold {self.empty_volume} units of liquid."
        else:
            return f"It holds {self.contained_volume} units of {self.liquid.name}," \
                   f" can hold {self.empty_volume} more."

    @property
    def effects(self) -> dict[str, int]:
        return self.liquid.effects

    @property
    def weight(self):
        if self.liquid is None:
            return self._own_weight
        else:
            return self._own_weight + self.liquid.weight * self.contained_volume

    @property
    def __class__(self) -> Type:
        if self.liquid is None:
            return LiquidContainer
        else:
            return self.liquid.__class__

    @property
    def empty_volume(self) -> int:
        empty_volume = self._max_volume - self.contained_volume
        if empty_volume < 0:
            raise ValueError(f"Container {self.name} is holding more than the max_volume!")
        return empty_volume

    def can_hold(self, substance: Item) -> bool:
        return isinstance(substance, Liquid) and \
            (self.liquid is None or self.liquid is substance)

    def fill(self, liquid: Liquid, volume: int) -> None:
        """Fills the container and returns the remainder amount to update the other container"""
        if self.liquid is not None and liquid is not self.liquid:
            raise ValueError("Container cannot hold more than one Liquid!")
        if volume < 1:
            raise ValueError(f"Container cannot be filled with {volume} volume of {liquid.name}!")
        if self.liquid is None:
            self.liquid = liquid
        if volume > self.empty_volume:
            raise ValueError(f"Container {self.name} cannot exceed max volume!")
        self.contained_volume += volume

    def decant(self, volume_to_decant) -> None:
        if volume_to_decant > self.contained_volume:
            raise ValueError(f"Container {self.name} asked to decant {volume_to_decant},"
                             f" but {self.contained_volume} available!")
        self.contained_volume -= volume_to_decant
        if self.contained_volume == 0:
            self.liquid = None


class SubstanceSource(Item):
    def __init__(self, name: str = "(substance source)",
                 description: str = '(empty source description)',
                 liquid: Liquid = None):
        super().__init__(name=name, icon='o', description=description, color=liquid.color)
        self.liquid = liquid
        self.contained_volume = 9999

    def decant(self, volume_to_decant) -> None:
        return


class WaterSkin(LiquidContainer):
    def __init__(self):
        super().__init__(name="an empty waterskin/skin of {}", max_volume=2, weight=1, icon=',',
                         color=config.brown_fg_color)


class Helmet(Item):
    pass


class Armor(Item):
    pass


class HideArmor(Armor):
    def __init__(self):
        super().__init__(name='hide armor', weight=5, icon='(', color=config.brown_fg_color,
                         description='Armor made from light hide')
        self.armor = 1
        self.combat_exhaustion = 1


class LeatherArmor(Armor):
    def __init__(self):
        super().__init__(name='leather armor', weight=6, icon='(', color=config.brown_fg_color,
                         description='Armor made from leather')
        self.armor = 3
        self.combat_exhaustion = 1


class PlateArmor(Armor):
    def __init__(self):
        super().__init__(name='plate armor', weight=15, icon='[', color=console.fg.default,
                         description='Armor made from metal plates')
        self.armor = 5
        self.combat_exhaustion = 5


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
    def __init__(self, damage: int = 0, combat_exhaustion: int = None, **kwargs):
        super().__init__(**kwargs)
        self.damage = damage
        self.combat_exhaustion = combat_exhaustion or self.weight


class RangedWeapon(MainHand):
    def __init__(self, ranged_weapon_type: str, skill: str, max_distance: int,
                 ranged_damage: int, **kwargs):
        super().__init__(**kwargs)
        self.ranged_weapon_type = ranged_weapon_type
        self.max_distance = max_distance
        self.skill = skill
        self.ranged_damage = ranged_damage

    def can_shoot(self, ammo: Optional[Item]) -> bool:
        return isinstance(ammo, RangedAmmo) and ammo.ranged_ammo_type == self.ranged_weapon_type


class Tool(MainHand):
    def __init__(self, skill: str, work_stat: str, work_exhaustion: int = None, **kwargs):
        super().__init__(**kwargs)
        self.skill = skill
        self.work_exhaustion = work_exhaustion or self.weight
        self.work_stat = work_stat


class AcornGun(RangedWeapon):
    def __init__(self, color=config.brown_fg_color):
        super().__init__(name='acorn gun', weight=4, icon='{', color=color,
                         description='A gun of dryadic design.',
                         ranged_damage=3, combat_exhaustion=2, ranged_weapon_type=config.acorn_gun_type,
                         skill=config.gun_skill, max_distance=15)


class Fist(Tool):
    def __init__(self):
        super().__init__(name="Your fist", description="Useful when you don't have a sword at hand.",
                         weight=0, icon='.', color=console.fg.lightblack,
                         work_exhaustion=2, skill=config.scavenging_skill, work_stat=config.Per,
                         damage=0, combat_exhaustion=1)


class TrollFist(Tool):
    def __init__(self):
        super().__init__(name="Your fist", description="You can break rocks for eating with it!",
                         weight=0, icon='.', color=console.fg.lightblack,
                         work_exhaustion=2, skill=config.mining_skill, work_stat=config.Str,
                         damage=1, combat_exhaustion=1)


class Pickaxe(Tool):
    def __init__(self):
        super().__init__(name="a pickaxe", description="Used to extract stone and ores",
                         weight=6, icon='/', color=console.fg.lightblack,
                         work_exhaustion=5, skill=config.mining_skill, work_stat=config.Str,
                         damage=1, combat_exhaustion=5)


class ShortSword(MainHand):
    def __init__(self, color=console.fg.default):
        super().__init__(name='short sword', weight=3, icon='|', color=color,
                         description='Made for stabbing.',
                         damage=3, combat_exhaustion=3)


class Offhand(Item):
    pass


class RangedAmmo(Offhand):
    def __init__(self, ranged_ammo_type: str, ranged_damage: int = 0, **kwargs):
        super().__init__(**kwargs)
        self.ranged_ammo_type = ranged_ammo_type
        self.ranged_damage = ranged_damage


class Acorn(RangedAmmo):
    def __init__(self):
        super().__init__(name='acorn', weight=1, icon='*', color=config.brown_fg_color,
                         is_stackable=True, description='The seed of an oak tree.',
                         ranged_damage=1, ranged_ammo_type=config.acorn_gun_type)


class ThrownWeapon(RangedWeapon, RangedAmmo):
    pass


class ThrowingKnife(ThrownWeapon):
    def __init__(self, color=console.fg.default):
        super().__init__(name='throwing knife', weight=1, icon='}', color=color,
                         description='A light knife, balanced for throwing.',
                         damage=1, ranged_damage=3, combat_exhaustion=1,
                         ranged_weapon_type=config.throwing_knife_skill, max_distance=7,
                         ranged_ammo_type=config.throwing_knife_skill, skill=config.throwing_knife_skill)


class AnimalWeapon(Item):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.combat_exhaustion = 1


class SmallTeeth(AnimalWeapon):
    def __init__(self):
        super().__init__(name='teeth', weight=1, icon=',', color=console.fg.default,
                         description='The teeth of a small animal')
        self.damage = 1


class MediumTeeth(AnimalWeapon):
    def __init__(self):
        super().__init__(name='teeth', weight=1, icon=',', color=console.fg.default,
                         description='The teeth of an animal')
        self.damage = 3


class MediumClaws(AnimalWeapon):
    def __init__(self):
        super().__init__(name='claws', weight=1, icon=',', color=console.fg.lightyellow,
                         description='The claws of an animal')
        self.damage = 3


class LargeClaws(AnimalWeapon):
    def __init__(self):
        super().__init__(name='large claws', weight=2, icon=',', color=console.fg.lightyellow,
                         description='The claws of a large animal')
        self.damage = 5


class HugeClaws(AnimalWeapon):
    def __init__(self):
        super().__init__(name='huge claws', weight=5, icon=',', color=console.fg.lightyellow,
                         description='The claws of a monstrous animal')
        self.damage = 10


class LargeTeeth(AnimalWeapon):
    def __init__(self):
        super().__init__(name='large teeth', weight=2, icon=',', color=console.fg.lightyellow,
                         description='The teeth of a large animal')
        self.damage = 5


class AnimalArmor(Item):
    pass


class LightHide(AnimalArmor):
    def __init__(self):
        super().__init__(name='light hide', weight=5, icon='(', color=config.brown_fg_color,
                         description='The light hide of an animal')
        self.armor = 1


class MediumHide(AnimalArmor):
    def __init__(self):
        super().__init__(name='medium hide', weight=10, icon='(', color=config.brown_fg_color,
                         description='The thick hide of an animal')
        self.armor = 3


class MediumScales(AnimalArmor):
    def __init__(self):
        super().__init__(name='medium scaly hide', weight=10, icon='(', color=console.fg.lightgreen,
                         description='The scaly hide of a lizard')
        self.armor = 3


class HeavyScales(AnimalArmor):
    def __init__(self):
        super().__init__(name='heavy scaled hide', weight=20, icon='(', color=console.fg.lightgreen,
                         description='The scaly hide of a monstrous lizard')
        self.armor = 8


class Feathers(AnimalArmor):
    def __init__(self):
        super().__init__(name='feathers', weight=3, icon=',', color=console.fg.lightblack,
                         description='The feathers of a bird')
        self.armor = 1


class RawMeat(Item):
    def __init__(self):
        super().__init__(name='raw meat', weight=1, icon=',', color=console.fg.red,
                         description="Not fit for eating, unless you're an ork!",
                         effects={config.sick_effect: 10,
                                  config.hunger_meat_effect: 5})


class Rock(Item):
    def __init__(self):
        super().__init__(name='rock', weight=2, icon='*', color=console.fg.lightblack,
                         description='Building material and throwing weapon',
                         effects={config.hunger_rock_effect: 10,
                                  config.thirst_rock_effect: 10},
                         is_stackable=True)


class IronOre(Item):
    def __init__(self):
        super().__init__(name='iron ore', weight=2, icon='*', color=console.fg.default,
                         description='Can be smelted and turned into metal bars',
                         effects={config.hunger_rock_effect: 20,
                                  config.thirst_rock_effect: 5})


class SilverOre(Item):
    def __init__(self):
        super().__init__(name='rock', weight=2, icon='*', color=console.fg.lightwhite,
                         description='Can be smelted and turned into metal bars',
                         effects={config.hunger_rock_effect: 5,
                                  config.thirst_rock_effect: 15})


class GoldOre(Item):
    def __init__(self):
        super().__init__(name='rock', weight=2, icon='*', color=console.fg.yellow,
                         description='Can be smelted and turned into metal bars',
                         effects={config.hunger_rock_effect: 5,
                                  config.thirst_rock_effect: 25})


class IceShard(Item):
    def __init__(self):
        super().__init__(name='rock', weight=2, icon='*', color=console.fg.lightblue,
                         description='Can be melted for drinking, or used to cool things')


class StilledWaterShard(Item):
    def __init__(self):
        super().__init__(name='stilled water', weight=2, icon='*', color=console.fg.white,
                         description='Used to meld still water equipment')


base_sentient_equipment_slots = {config.head_slot: Helmet, config.armor_slot: Armor,
                                 config.main_hand_slot: MainHand, config.offhand_slot: Offhand,
                                 config.back_slot: Back, config.boots_slot: Boots}
base_animal_equipment_slots = {config.animal_weapon_slot: AnimalWeapon,
                               config.animal_armor_slot: AnimalArmor,
                               config.animal_meat_slot: RawMeat}


# The species define what a creature is physically and how it looks in the game
# This also includes the "equipment" of animal species which is part of the body
class Species(GameObject):
    """Defines what a creature is and how it acts"""

    _equipment_slots = {}
    initial_equipment = ()

    def __init__(self, custom_ai: dict[str, list[str]] = None,
                 initial_disposition: str = config.indifferent_disposition,
                 base_effect_modifiers: dict[str, int] = None,
                 active_effects: dict[str, int] = None,
                 consumable_types: list[Type[Item]] = None,
                 fist_weapon: Type[Item] = Fist,
                 base_skills: dict[str, int] = None,
                 **kwargs):
        super().__init__(**kwargs)
        basic_ai = {config.indifferent_disposition: [config.random_behavior],
                    config.fearful_disposition: [config.run_from_humanoid_behavior,
                                                 config.random_behavior],
                    config.aggressive_disposition: [config.chase_humanoid_behavior,
                                                    config.random_behavior]}
        if custom_ai is not None:
            basic_ai.update(custom_ai)
        self.initial_disposition = initial_disposition
        self.ai = basic_ai
        self.base_skills = base_skills or {}
        self.fist_weapon: Item = fist_weapon()
        self.base_effect_modifiers = base_effect_modifiers or {}
        self.active_effects = {config.non_rest_energy_regen_effect: 1}
        if active_effects is not None:
            self.active_effects.update(active_effects)
        if consumable_types is None:
            self.consumable_types = [RawMeat, Liquid]
        else:
            self.consumable_types = consumable_types

    @property
    def base_stats(self) -> dict[str, int]:
        raise NotImplementedError(f'Class {self.__class__} must implement base stats!')

    @property
    def equipment_slots(self):
        return self._equipment_slots


class HumanoidSpecies(Species):
    @property
    def base_stats(self) -> dict[str, int]:
        return make_stats(default=5)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        sentient_races.append(self)
        self._equipment_slots = base_sentient_equipment_slots.copy()


class AnimalSpecies(Species):
    @property
    def base_stats(self) -> dict[str, int]:
        return self._base_stats

    def __init__(self, base_stats: dict[str, int] = None, equipment: list[Type[Item]] = (), **kwargs):
        if 'initial_disposition' not in kwargs:
            kwargs['initial_disposition'] = config.fearful_disposition
        super().__init__(**kwargs)
        self.initial_equipment = equipment
        self._base_stats = base_stats or make_stats(default=1, stats={config.Per: 5})
        self._equipment_slots = base_animal_equipment_slots.copy()


human_race = HumanoidSpecies(name=config.Human,
                             icon='H',
                             color=config.order_color,
                             description=knowledge[config.Human][0],
                             sort_key=0,
                             base_effect_modifiers={config.travel_energy_loss_modifier: 0})
dwarf_race = HumanoidSpecies(name=config.Dwarf,
                             icon='D',
                             color=config.order_color,
                             description=knowledge[config.Dwarf][0],
                             sort_key=1,
                             base_effect_modifiers={config.drunk_effect: -20, config.armor_modifier: 1.2})
gnome_race = HumanoidSpecies(name=config.Gnome,
                             icon='G',
                             color=config.order_color,
                             description=knowledge[config.Gnome][0],
                             sort_key=2)
elf_race = HumanoidSpecies(name=config.Elf,
                           icon='E',
                           color=config.order_color,
                           description=knowledge[config.Elf][0],
                           sort_key=3,
                           base_effect_modifiers={config.max_mana_modifier: 1.2})
orc_race = HumanoidSpecies(name=config.Orc,
                           icon='O',
                           color=config.chaos_color,
                           description=knowledge[config.Orc][0],
                           sort_key=4,
                           base_effect_modifiers={config.sick_effect: -20})
troll_race = HumanoidSpecies(name=config.Troll,
                             icon='T',
                             color=config.chaos_color,
                             description=knowledge[config.Troll][0],
                             sort_key=5, consumable_types=[Rock],
                             base_effect_modifiers={config.max_hp_modifier: 1.2},
                             fist_weapon=TrollFist)
goblin_race = HumanoidSpecies(name=config.Goblin,
                              icon='G',
                              color=config.chaos_color,
                              description=knowledge[config.Goblin][0],
                              sort_key=6, base_effect_modifiers={config.max_load_modifier: 1.2,
                                                                 config.scavenging_skill: 1.3})
kraken_race = HumanoidSpecies(name=config.Kraken,
                              icon='K',
                              color=config.chaos_color,
                              description=knowledge[config.Kraken][0],
                              sort_key=7)
imp_race = HumanoidSpecies(name=config.Imp,
                           icon='I',
                           color=config.chaos_color,
                           description=knowledge[config.Imp][0],
                           sort_key=8)
dryad_race = HumanoidSpecies(name=config.Dryad,
                             icon='D',
                             color=config.nature_color,
                             description=knowledge[config.Dryad][0],
                             sort_key=9)
shifter_race = HumanoidSpecies(name=config.Shifter,
                               icon='S',
                               color=config.nature_color,
                               description=knowledge[config.Shifter][0],
                               sort_key=10,
                               active_effects={config.non_rest_hp_regen_effect: 1})
water_elemental_race = HumanoidSpecies(name=config.WaterElemental,
                                       icon='W',
                                       color=config.nature_color,
                                       description=knowledge[config.WaterElemental][0],
                                       sort_key=11,
                                       base_effect_modifiers={config.hunger_water_effect: 20})
fae_race = HumanoidSpecies(name=config.Fae,
                           icon='F',
                           color=config.nature_color,
                           description=knowledge[config.Fae][0],
                           sort_key=12,
                           base_effect_modifiers={config.hunger_meat_effect: -20})
field_mouse_species = AnimalSpecies(name='field mouse', icon='m', color=config.brown_fg_color,
                                    description='A field mouse.')
rat_species = AnimalSpecies(name='rat', icon='r', color=console.fg.lightblack,
                            description='A big rat.', equipment=[RawMeat])
snow_hare_species = AnimalSpecies(name='snow hare', icon='h', color=console.fg.lightwhite,
                                  description='A snow hare.', equipment=[RawMeat])
ash_beetle_species = AnimalSpecies(name='ash beetle', icon='b', color=console.fg.lightblack,
                                   description='An ash beetle')
ice_mantis_species = AnimalSpecies(name='ice mantis', icon='m', color=console.fg.blue,
                                   description='An ice mantis.')
sand_snake_species = AnimalSpecies(name='sand snake', icon='s', color=console.fg.yellow,
                                   description='A desert snake', equipment=[RawMeat])
scorpion_species = AnimalSpecies(name='scorpion', icon='s', color=console.fg.lightblack,
                                 description='A black scorpion')
fox_species = AnimalSpecies(name='fox', icon='f', color=console.fg.lightred,
                            description='A fox.',
                            equipment=[RawMeat, SmallTeeth, LightHide])
jaguar_species = AnimalSpecies(name='jaguar', icon='j', color=console.fg.lightyellow,
                               description='A jaguar.',
                               base_stats=make_stats(8, {config.Str: 5, config.End: 6, config.Wil: 1}),
                               equipment=[RawMeat, MediumTeeth, LightHide],
                               initial_disposition=config.aggressive_disposition)
wolf_species = AnimalSpecies(name='wolf', icon='w', color=console.fg.lightblack,
                             description='A wolf.',
                             base_stats=make_stats(4, {config.Dex: 7, config.Per: 8, config.Wil: 1}),
                             equipment=[RawMeat, MediumTeeth, LightHide],
                             initial_disposition=config.aggressive_disposition)
winter_wolf_species = AnimalSpecies(name='winter wolf', icon='w', color=console.fg.white,
                                    description='A white wolf.',
                                    base_stats=make_stats(4, {config.Dex: 7, config.Per: 8, config.Wil: 1}),
                                    equipment=[RawMeat, MediumTeeth, LightHide],
                                    initial_disposition=config.aggressive_disposition)
ice_bear_species = AnimalSpecies(name='ice bear', icon='b', color=console.fg.lightblue,
                                 description='A polar bear!',
                                 base_stats=make_stats(10, {config.Dex: 3, config.Per: 5, config.Wil: 1}),
                                 equipment=[RawMeat, LargeClaws, MediumHide],
                                 initial_disposition=config.aggressive_disposition)
bear_species = AnimalSpecies(name='bear', icon='b', color=config.brown_fg_color,
                             description='A big bear!',
                             base_stats=make_stats(10, {config.Dex: 3, config.Per: 5, config.Wil: 1}),
                             equipment=[RawMeat, LargeClaws, MediumHide],
                             initial_disposition=config.aggressive_disposition)
swamp_dragon_species = AnimalSpecies(name='swamp dragon', icon='d', color=console.fg.lightgreen,
                                     description='A swamp dragon!',
                                     base_stats=make_stats(10, {config.Dex: 5, config.Per: 6, config.Wil: 1}),
                                     equipment=[RawMeat, LargeTeeth, MediumScales],
                                     initial_disposition=config.aggressive_disposition)
crocodile_species = AnimalSpecies(name='crocodile', icon='c', color=console.fg.lightgreen,
                                  description='A big crocodile!',
                                  base_stats=make_stats(6, {config.Dex: 4, config.Per: 4, config.Wil: 1}),
                                  equipment=[RawMeat, LargeTeeth, MediumScales],
                                  initial_disposition=config.aggressive_disposition)
monkey_species = AnimalSpecies(name='monkey', icon='m', color=console.fg.lightred,
                               description='A monkey.',
                               equipment=[RawMeat, SmallTeeth, LightHide])
ice_fox_species = AnimalSpecies(name='ice fox', icon='f', color=console.fg.blue,
                                description='An ice fox.',
                                equipment=[RawMeat, SmallTeeth, LightHide])
eagle_species = AnimalSpecies(name='eagle', icon='e', color=config.brown_fg_color,
                              description='An eagle.',
                              base_stats=make_stats(4, {config.Dex: 10, config.Per: 15, config.Wil: 1}),
                              equipment=[RawMeat, MediumClaws, Feathers],
                              initial_disposition=config.aggressive_disposition)
hydra_species = AnimalSpecies(name='hydra', icon='H', color=console.fg.lightgreen,
                              description='A giant hydra!',
                              base_stats=make_stats(stats={config.Dex: 15, config.Per: 16, config.Wil: 15,
                                                           config.Str: 18, config.End: 14}),
                              equipment=[RawMeat, HugeClaws, HeavyScales],
                              initial_disposition=config.aggressive_disposition)


# Flavor terrain rare creatures?


class Creature(GameObject):
    """Defines how a creature interacts with the environment"""

    def __init__(self, species: Species, **kwargs):
        if kwargs.get('icon') is None:
            kwargs['icon'] = species.raw_icon
        if kwargs.get('color') is None:
            kwargs['color'] = species.color
        if kwargs.get('name') is None:
            kwargs['name'] = species.name
        super().__init__(**kwargs)
        self.species = species
        if self.description == config.empty_string:
            self._description = self.species.description
        self._disposition = self.species.initial_disposition
        self._ai = self.species.ai
        self._skills = self.species.base_skills.copy()
        self.stats = self.species.base_stats.copy()
        self._effect_modifiers = self.species.base_effect_modifiers
        self._active_effects: dict[str, int] = self.species.active_effects
        self.equipment_slots = self.species.equipment_slots
        self.equipped_items = {k: empty_space for k in self.equipment_slots}
        for item_type in self.species.initial_equipment:
            self.swap_equipment(item_type())
        # TODO: Add ageing for NPCs here between the stats and the sub-stats
        self._hp = self.max_hp
        self._mana = self.max_mana
        self._energy = self.max_energy
        self._hunger: int = 0
        self._thirst: int = 0
        self._sustenance_needs: int = 0
        self._age: int = 0
        self.ranged_target: Optional[Union[Creature, tuple[int, int]]] = None

    @property
    def effective_equipment(self) -> dict:
        return self.equipped_items

    @property
    def perception_radius(self) -> int:
        return self.stats[config.Per]

    @property
    def load(self) -> int:
        return sum([item.weight for item in self.equipped_items.values()])

    @property
    def melee_damage(self) -> int:
        return random.randint(1, max(self.stats[config.Str] // 4, 1)) + self.weapon_damage()

    @property
    def armor(self) -> int:
        return random.randint(int(self.equipment_armor() * self.stats[config.Dex] / config.max_stat_value),
                              self.equipment_armor())

    def equipment_armor(self) -> int:
        armor = 0
        for item in self.effective_equipment.values():
            try:
                armor += item.armor
            except AttributeError:
                pass
        return int(armor * self._effect_modifiers.get(config.armor_modifier, 1))

    def weapon_damage(self) -> int:
        dmg = 0
        for item in self.effective_equipment.values():
            try:
                dmg += item.damage
            except AttributeError:
                pass
        dmg = int(dmg * self._exhaustion_modifier)
        return dmg

    @property
    def _combat_exhaustion(self) -> int:
        exhaustion = 0
        for item in self.effective_equipment.values():
            if hasattr(item, 'combat_exhaustion'):
                exhaustion += item.combat_exhaustion
        return exhaustion

    @property
    def hp(self) -> int:
        return self._hp

    @hp.setter
    def hp(self, value):
        self._hp = min(self.max_hp, value)

    @property
    def energy(self) -> int:
        return self._energy

    @energy.setter
    def energy(self, value):
        difference = self._energy - value
        if difference > 0:
            self._get_hungry(difference)
        self._energy = min(self.max_energy - self.current_max_energy, max(0, value))

    def _get_hungry(self, change):
        """Add hunger and thirst on every 100 points of energy spent or every 100 turns"""
        self._sustenance_needs += change
        if self._sustenance_needs >= 100:
            famine = self._sustenance_needs // 100
            self.hunger += famine
            self.thirst += famine
            self._sustenance_needs = self._sustenance_needs % 100

    @property
    def hunger(self):
        return self._hunger

    @hunger.setter
    def hunger(self, value):
        self._hunger = min(50, max(0, value))

    @property
    def thirst(self):
        return self._thirst

    @thirst.setter
    def thirst(self, value):
        self._thirst = min(50, max(0, value))

    @property
    def sustenance_modifier(self) -> int:
        return (self.hunger + self.thirst) // 10 * 10

    @property
    def _exhaustion_modifier(self) -> float:
        return 0.5 + 0.5 * self.energy / self.max_energy

    @property
    def mana(self) -> int:
        return self._mana

    @mana.setter
    def mana(self, value):
        self._mana = min(self.max_mana, value)

    @property
    def max_hp(self) -> int:
        base_hp = self.stats[config.Str] + 2 * self.stats[config.End]
        return int(base_hp * self._effect_modifiers.get(config.max_hp_modifier, 1))

    @property
    def max_mana(self) -> int:
        base_mana = self.stats[config.Wil] * 10
        return int(base_mana * self._effect_modifiers.get(config.max_mana_modifier, 1))

    @property
    def max_energy(self) -> int:
        return self.stats[config.End] * 10

    @property
    def current_max_energy(self) -> int:
        return self.max_energy * self.sustenance_modifier // 100

    def confirm_movement_direction(self, direction: str) -> str:
        """Apply effects that might change the direction of movement"""
        rose_of_directions = '12369874'
        if config.drunk_effect in self._active_effects:
            direction_index = rose_of_directions.index(direction)
            new_index = direction_index + random.randint(-1, 1)
            if new_index == len(rose_of_directions):
                new_index = 0
            return rose_of_directions[new_index]
        return direction

    def travel(self) -> None:
        fraction = self._effect_modifiers.get(config.travel_energy_loss_modifier, self.load / self.max_load)
        energy_to_lose = int(self.max_energy * fraction) // 2
        self.energy -= energy_to_lose
        self.ranged_target = None

    def live(self) -> None:
        """
        Tick effects like sickness/poison/regen/regular non-rest energy regain
        Effects with values of 0 or lower are removed
        """
        self._age += 1
        self._get_hungry(1)
        for effect, value in self._active_effects.items():
            if effect in [config.sick_effect, config.drunk_effect]:
                if random.random() > value / (value + self.stats[config.End]):
                    self._active_effects[effect] -= 1
            elif effect == config.non_rest_energy_regen_effect:
                if random.randint(0, config.max_stat_value) <= self.stats[config.End]:
                    self.energy += 1
            elif effect == config.non_rest_hp_regen_effect:
                if random.randint(0, config.max_stat_value) <= self.stats[config.End] / 2:
                    self.hp += 1
            else:
                raise ValueError(f"Unhandled effect '{effect}'!")
        for effect, value in list(self._active_effects.items()):
            if value <= 0:
                self._active_effects.pop(effect)

    def can_consume(self, item: Item) -> bool:
        return any([isinstance(item, consumable_type) for consumable_type in self.species.consumable_types])

    def apply_effects(self, effects: dict[str, int]) -> None:
        """
        Personalized effect values are created through the _effect_modifiers dictionary that
        depends on the race and the actions of the character.
        """
        for name, effect in effects.items():
            self._apply_effect(name, effect + self._effect_modifiers.get(name, 0))

    def _apply_effect(self, name: str, effect_size: int) -> None:
        """
        Effects are treated in groups based on the name prefix.
        """
        if effect_size <= 0:
            return
        if name.startswith(config.hunger_effect_prefix):
            self.hunger -= max(0, effect_size - self._active_effects.get(config.sick_effect, 0))
        elif name.startswith(config.thirst_effect_prefix):
            self.thirst -= max(0, effect_size - self._active_effects.get(config.sick_effect, 0))
        elif name == config.normal_damage_effect:
            self._receive_normal_damage(effect_size)
        else:
            self._active_effects[name] = \
                self._active_effects.get(name, 0) + effect_size

    def get_statuses(self) -> list[str]:
        statuses = []
        if self.hunger >= 5:
            statuses.append(console.fg.red + 'Hungry' + console.fx.end)
        if self.thirst >= 5:
            statuses.append(console.fg.red + 'Thirsty' + console.fx.end)
        for effect in self._active_effects:
            if effect in config.visible_effects:
                statuses.append(console.fg.green + effect + console.fx.end)
        return statuses

    @property
    def max_load(self) -> int:
        base_load = self.stats[config.Str] * 5
        return int(base_load * self._effect_modifiers.get(config.max_load_modifier, 1))

    @property
    def bag(self):
        return self.equipped_items[config.back_slot]

    def can_equip(self, item: Item) -> bool:
        return any([isinstance(item, slot_type) for slot_type in self.equipment_slots.values()])

    def can_carry(self, item: Item) -> bool:
        return item.weight <= self.max_load - self.load

    def can_carry_stack_or_item(self, item: Item) -> bool:
        if not isinstance(item, ItemStack):
            return self.can_carry(item)
        single_unit = item.items[0]
        return self.can_carry(single_unit)

    def allowed_split_size(self, item_stack: ItemStack) -> int:
        return (self.max_load - self.load) // item_stack.items[0].weight

    def can_swap_equipment(self, item: Item) -> bool:
        if isinstance(item, ItemStack):
            item = item.items[0]
        for slot, slot_type in self.equipment_slots.items():
            if isinstance(item, slot_type):
                available_load = self.max_load - self.load
                load_difference = item.weight - self.equipped_items[slot].weight
                return available_load >= load_difference
        return False

    def weight_gained_by_swapping_equipment(self, item: Item) -> int:
        for slot, slot_type in self.equipment_slots.items():
            if isinstance(item, slot_type):
                return self.equipped_items[slot].weight
        raise TypeError(f"Item {item.name} cannot be equipped in any slot!")

    def swap_equipment(self, item: Item) -> Item:
        for slot, slot_type in self.equipment_slots.items():
            if isinstance(item, slot_type):
                old_item = self.equipped_items[slot]
                self.equipped_items[slot] = item
                return old_item

    def get_goals(self) -> list[str]:
        return self._ai[self._disposition]

    def get_drops(self):
        return [item for item in self.equipped_items.values() if item is not empty_space]

    def bump_with(self, other_creature: 'Creature') -> None:
        if self._disposition == config.aggressive_disposition or self.raw_icon == '@':
            self.energy -= self._combat_exhaustion
            hit_effects = {config.normal_damage_effect: self.melee_damage}
            other_creature.apply_effects(hit_effects)

    def _receive_normal_damage(self, damage: int) -> None:
        load_modifier = (self.max_load - self.load) / self.max_load
        dex_modifier = self.stats[config.Dex] / config.max_stat_value
        dodge_chance = dex_modifier * load_modifier * self._exhaustion_modifier
        if random.random() > dodge_chance:
            self.hp -= max(0, damage - self.armor)

    def rest(self):
        self.energy += random.randint(1, max(self.stats[config.End] // 5, 1))
        if random.random() < (self.stats[config.End] / config.max_stat_value / 2) * (self.energy / self.max_energy):
            self.hp += 1

    @property
    def is_dead(self) -> bool:
        return self.hp <= 0

    def get_stats_data(self) -> dict[str, str]:
        return {stat: f'{value:.2f}' for stat, value in self.stats.items()}

    def get_secondary_stats_data(self) -> dict[str, str]:
        return {'Hitpoints': f'{self.hp}/{self.max_hp}',
                'Mana': f'{self.mana}/{self.max_mana}',
                'Energy': f'{self.energy}/{self.max_energy}',
                'Load': f'{self.load}/{self.max_load}'
                }

    def _effective_skill(self, skill_name: str) -> int:
        raw_skill = self._skills.get(skill_name, 0)
        modifier = self._effect_modifiers.get(skill_name, 1)
        return int(raw_skill * modifier)

    def get_skills_data(self) -> dict[str, int]:
        return {skill: self._effective_skill(skill) for skill in self._skills}


class Animal(Creature):
    def __init__(self, species: AnimalSpecies, **kwargs):
        super().__init__(species, **kwargs)


class Humanoid(Creature):
    def __init__(self, species: HumanoidSpecies, **kwargs):
        super().__init__(species, **kwargs)

    @property
    def description(self) -> str:
        if self.raw_icon == '@':
            return self._description
        member = "An" if self.species.name[0] in 'EIO' else "A"
        return f"{member} {self.species.name}."

    @property
    def effective_equipment(self) -> dict:
        effective_items = {**self.equipped_items}
        if effective_items[config.main_hand_slot] is empty_space:
            effective_items[config.main_hand_slot] = self.species.fist_weapon
        return effective_items

    def _get_ranged_weapon(self) -> Optional[RangedWeapon]:
        for slot in [config.main_hand_slot, config.offhand_slot]:
            item = self.effective_equipment[slot]
            if isinstance(item, RangedWeapon):
                return item
        return None

    def _get_ranged_ammo(self) -> Optional[RangedAmmo]:
        for slot in [config.main_hand_slot, config.offhand_slot]:
            item = self.effective_equipment[slot]
            if isinstance(item, RangedAmmo):
                return item
        return None

    def get_shooting_range(self) -> int:
        ranged_weapon = self._get_ranged_weapon()
        if ranged_weapon is not None:
            return ranged_weapon.max_distance
        return 0

    def can_shoot_or_throw(self) -> Optional[str]:
        ranged_weapon = self._get_ranged_weapon()
        ammo = self._get_ranged_ammo()
        if ranged_weapon is None:
            return "You don't have a ranged weapon equipped!"
        if ammo is None:
            return "You don't have ammunition!"
        if not ranged_weapon.can_shoot(ammo):
            return "Your ammo and weapon don't match!"
        return

    @property
    def _ranged_damage(self) -> int:
        ranged_weapon = self._get_ranged_weapon()
        ammo = self._get_ranged_ammo()
        if ranged_weapon is ammo:
            weapon_damage = ranged_weapon.ranged_damage
        else:
            weapon_damage = ranged_weapon.ranged_damage + ammo.ranged_damage
        stats = (self.stats[config.Dex] + self.stats[config.Per]) // 2
        return random.randint(0, max(stats // 2, 1)) + weapon_damage

    def shoot(self) -> tuple[RangedAmmo, int, dict[str, int]]:
        weapon = self._get_ranged_weapon()
        ammo = self._get_ranged_ammo()
        effects = {config.normal_damage_effect: self._ranged_damage}
        current_skill = self._effective_skill(weapon.skill)
        self._increase_skill(weapon.skill)
        for slot, item in self.equipped_items.items():
            if item is ammo:
                if isinstance(item, ItemStack):
                    ammo = item.split(1)
                    if item.is_empty:
                        self.equipped_items[slot] = empty_space
                else:
                    self.equipped_items[slot] = empty_space
        self.energy -= self._combat_exhaustion // 2
        return ammo, current_skill, effects

    def _increase_skill(self, skill_name: str) -> None:
        current_skill = self._skills.get(skill_name, 0)
        if not random.randint(0, 3) and random.random() > current_skill / config.max_skill_value:
            self._skills[skill_name] = self._skills.get(skill_name, 0) + 1
            if self._skills[skill_name] > config.max_skill_value:
                self._skills[skill_name] = config.max_skill_value

    def _increase_stat(self, stat_name: str) -> None:
        current_stat = self.stats[stat_name]
        if not random.randint(0, 3) and current_stat < config.max_stat_value:
            self.stats[stat_name] += 0.01
            if self.stats[stat_name] > config.max_stat_value:
                self.stats[stat_name] = config.max_stat_value

    def _improve(self, skill_name: str, stat_name: str) -> None:
        self._increase_skill(skill_name)
        self._increase_stat(stat_name)

    def work_on(self, tile: 'Tile') -> tuple[list[Item], str]:
        for slot in [config.main_hand_slot]:
            item = self.effective_equipment[slot]
            if isinstance(item, Tool) and item.skill in tile.applicable_skills:
                if item.work_exhaustion > self.energy:
                    return [], "You are too tired to work!"
                current_skill = self._effective_skill(item.skill)
                skill_strength = int(self.stats[item.work_stat] + current_skill / 10)
                self.energy -= item.work_exhaustion
                self._improve(item.skill, item.work_stat)
                result = tile.apply_skill(item.skill, strength=skill_strength)
                return result
        else:
            return [], "You don't have the right tools."

    def can_stack_equipment(self, item: Item) -> bool:
        for slot, equipped_item in self.equipped_items.items():
            try:
                _ = ItemStack([item, equipped_item])
                return True
            except TypeError:
                pass
        return False

    def stack_equipment(self, item: Item) -> None:
        if not item.is_stackable:
            raise TypeError(f"Item {item.name} is not stackable!")
        for slot, equipped_item in self.equipped_items.items():
            try:
                new_stack = ItemStack([equipped_item, item])
                self.equipped_items[slot] = new_stack
                return
            except TypeError:
                pass
        raise TypeError(f"Could not find equipment slot to stack {item.name}!")


class Game:
    """
    Keep the game state: All elements that can change their own state (Creatures, effects, crops, etc.)
    """
    welcome_state = 'welcome'
    new_game_state = 'starting_new_game'
    loading_state = 'loading_existing_game'
    character_name_substate = 'getting_character_name'
    race_selection_substate = 'character_race_selection'
    playing_state = 'playing'
    scene_substate = 'game_scene'
    map_substate = 'world_map'
    equip_for_substate = 'equip_for_screen'
    inventory_substate = 'inventory_substate'
    fill_container_substate = 'fill_container_substate'
    working_substate = 'working_substate'
    looking_substate = 'looking_substate'
    character_sheet_substate = 'character_sheet_substate'
    high_score_state = 'high_score'
    ended_state = 'ended'
    races = sentient_races

    def __init__(self):
        self._turn = 0
        self.character: Optional[Humanoid] = None
        self._current_location: Optional[Location] = None
        self.character_name: Optional[str] = None
        self._last_character_target = None
        self._equipping_slot: Optional[str] = None
        self._selected_ground_item: Item = empty_space
        self._selected_bag_item: Item = empty_space
        self.selected_equipped_item_index: int = 0
        self._ground_container: Optional[PhysicalContainer] = None
        self._container_to_fill: Optional[LiquidContainer] = None
        self.active_inventory_container_name = self.get_ground_name()
        self._creature_coords: dict[tuple[int, int], Creature] = {}
        self.world: Optional[World] = None
        self.state: str = Game.welcome_state
        self.substate: Optional[str] = None
        self._new_message: str = ''
        self._current_message: str = ''
        self._observed_target: Optional[tuple[int, int]] = None
        self._sub_turn_effects: dict = {}

    @property
    def _selected_equipped_item(self):
        return list(self.character.equipped_items.values())[self.selected_equipped_item_index]

    def start_game(self, character_race) -> None:
        if character_race is None:
            return
        self.character = Humanoid(name=self.character_name, species=character_race,
                                  description='You are standing here.', color=console.fg.default,
                                  icon='@')
        # TODO: This is the initial testing configuration. Add the selected starting location here.
        initial_coords = (0, 0)
        self._current_location = self.world.get_location(initial_coords)
        character_coords = self._current_location.get_empty_spot_for(self.character)
        self._creature_coords[character_coords] = self.character
        self._creature_coords = self._current_location.load_creatures(self._creature_coords, self._turn)

        self._current_location.put_item(Bag(), character_coords)
        self._current_location.put_item(ShortSword(color=console.fg.red), character_coords)
        self._current_location.put_item(ThrowingKnife(), character_coords)
        self._current_location.put_item(AcornGun(), character_coords)
        for i in range(10):
            self._current_location.put_item(Acorn(), character_coords)
        for i in range(10):
            self._current_location.put_item(Rock(), character_coords)
        self._current_location.put_item(PlateArmor(), character_coords)

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
        if self.state == Game.welcome_state:
            return {commands.NewGame(): self._new_game,
                    commands.LoadGame(): self._initiate_load}
        elif self.state == Game.playing_state and self.substate == Game.working_substate:
            return {commands.Stop(): self._go_to_normal_mode,
                    commands.Rest(): self._character_rests,
                    commands.Move(): self._player_work}
        elif self.state == Game.playing_state and self.substate == Game.looking_substate:
            return {commands.Stop(): self._go_to_normal_mode,
                    commands.Move(): self._move_observed_target,
                    commands.Target(): self._set_character_ranged_target}
        elif self.state == Game.playing_state and self.substate == Game.scene_substate:
            return {commands.Move(): self._character_moves,
                    commands.Rest(): self._character_rests,
                    commands.Map(): self._open_map,
                    commands.Inventory(): self._open_inventory,
                    commands.Work(): self._go_to_work_mode,
                    commands.Look(): self._go_to_look_mode,
                    commands.Shoot(): self._character_shoots,
                    commands.CharacterSheet(): self._open_character_sheet}
        elif self.state == Game.playing_state and self.substate == Game.map_substate:
            return {commands.Close(): self._back_to_scene}
        elif self.state == Game.playing_state and self.substate == Game.character_sheet_substate:
            return {commands.Close(): self._back_to_scene}
        elif self.state == Game.playing_state and self.substate == Game.inventory_substate:
            inventory_commands = {commands.Close(): self._back_to_scene}
            # "From ground" commands
            if self.active_inventory_container_name == self.get_ground_name():
                if self.character.bag is not empty_space \
                        and self.character.bag.has_space() \
                        and self.character.can_carry_stack_or_item(self._selected_ground_item) \
                        and self._selected_ground_item is not empty_space:
                    inventory_commands[commands.InventoryPickUp()] = self._pick_up_item
                if self.character.can_stack_equipment(self._selected_ground_item) \
                        and self.character.can_carry_stack_or_item(self._selected_ground_item):
                    inventory_commands[commands.InventoryEquip()] = self._stack_equip_from_ground_in_inventory_screen
                elif self.character.can_swap_equipment(self._selected_ground_item):
                    inventory_commands[commands.InventoryEquip()] = self._equip_from_ground_in_inventory_screen
                if self.character.can_consume(self._selected_ground_item):
                    inventory_commands[commands.InventoryConsume()] = self._consume_from_ground_in_inventory_screen
                if isinstance(self._selected_ground_item, LiquidContainer) \
                        and self._selected_ground_item.empty_volume > 0:
                    inventory_commands[commands.InventoryFill()] = self._fill_from_ground_in_inventory_screen
                if isinstance(self._selected_ground_item, LiquidContainer) \
                        and self._selected_ground_item.contained_volume > 0:
                    inventory_commands[commands.InventoryEmpty()] = self._empty_from_ground_in_inventory_screen
            # "From bag" commands
            if self.active_inventory_container_name == self.get_bag_name():
                if self._selected_bag_item is not empty_space \
                        and (self._ground_container.has_space()
                             or isinstance(self._ground_container, Tile)):
                    inventory_commands[commands.InventoryDrop()] = self._drop_from_inventory_screen
                if self.character.can_stack_equipment(self._selected_bag_item):
                    inventory_commands[commands.InventoryEquip()] = self._stack_equip_from_bag_in_inventory_screen
                elif self.character.can_equip(self._selected_bag_item):
                    inventory_commands[commands.InventoryEquip()] = self._equip_from_bag_in_inventory_screen
                if self.character.can_consume(self._selected_bag_item):
                    inventory_commands[commands.InventoryConsume()] = self._consume_from_bag_in_inventory_screen
                if isinstance(self._selected_bag_item, LiquidContainer) \
                        and self._selected_bag_item.empty_volume > 0:
                    inventory_commands[commands.InventoryFill()] = self._fill_from_bag_in_inventory_screen
                if isinstance(self._selected_bag_item, LiquidContainer) \
                        and self._selected_bag_item.contained_volume > 0:
                    inventory_commands[commands.InventoryEmpty()] = self._empty_from_bag_in_inventory_screen
            # "From equipment" commands
            if self.active_inventory_container_name == config.equipment_title:
                if self._selected_equipped_item is not empty_space \
                        and ((self.character.bag is not empty_space and self.character.bag.has_space())
                             or (self._ground_container.has_space()
                                 or isinstance(self._ground_container, Tile))):
                    inventory_commands[commands.InventoryUnequip()] = self._unequip_from_inventory_screen
                if self._selected_equipped_item is empty_space:
                    inventory_commands[commands.InventoryEquipSlot()] = self._equip_for_slot_from_inventory_screen
            return inventory_commands
        else:
            return {}

    def _open_character_sheet(self, _) -> bool:
        self.substate = Game.character_sheet_substate
        return True

    def _character_shoots(self, _) -> bool:
        ranged_response = self.character.can_shoot_or_throw()
        if ranged_response is not None:
            self._add_message(ranged_response)
        else:
            target = self.character.ranged_target or self._last_character_target
            if target is None:
                self._add_message("No target selected!")
            else:
                if isinstance(target, Creature):
                    target = self._get_coords_of_creature(target)
                character_position = self._get_coords_of_creature(self.character)
                distance = coord_distance(character_position, target)
                max_distance = self.character.get_shooting_range()
                if distance > max_distance:
                    self._add_message("The target is beyond your weapon's range!")
                else:
                    projectile, skill, effects = self.character.shoot()
                    max_deviation = int(
                        (max_distance / 5)
                        * ((config.max_skill_value - skill) / config.max_skill_value)
                        * ((max_distance - distance) / max_distance))
                    max_deviation = max(max_deviation, 1)
                    x_deviation = random.randint(0, max_deviation) * random.choice([-1, 1])
                    y_deviation = random.randint(0, max_deviation) * random.choice([-1, 1])
                    final_target = (target[0] + y_deviation, target[1] + x_deviation)
                    while not self._current_location.contains_coords(final_target):
                        x_deviation = random.randint(0, max_deviation) * random.choice([-1, 1])
                        y_deviation = random.randint(0, max_deviation) * random.choice([-1, 1])
                        final_target = (target[0] + y_deviation, target[1] + x_deviation)
                    projectile_path = direct_path(character_position, final_target)[1:]
                    flying_projectile = {'item': projectile, 'path': projectile_path,
                                         'effects': effects}
                    self._sub_turn_effects[projectile_path[0]] = flying_projectile
        self._living_world()
        return True

    def _set_character_ranged_target(self, _) -> bool:
        self.character.ranged_target = self._creature_coords.get(self._observed_target,
                                                                 self._observed_target)
        return True

    def _go_to_look_mode(self, _) -> bool:
        self.substate = Game.looking_substate
        self._observed_target = self._get_coords_of_creature(self.character)
        return True

    def _move_observed_target(self, direction) -> bool:
        new_coords = calculate_new_position(self._observed_target, direction, *self.world.size)
        if self.world.get_location(new_coords) is not self._current_location:
            return True
        else:
            self._observed_target = new_coords
        return True

    def _player_work(self, direction: str) -> bool:
        self._character_labor(direction)
        self._living_world()
        return True

    def _go_to_normal_mode(self, _) -> bool:
        self.substate = Game.scene_substate
        return True

    def _go_to_work_mode(self, _) -> bool:
        self.substate = Game.working_substate
        return True

    def _empty_from_bag_in_inventory_screen(self, _) -> bool:
        if isinstance(self._selected_bag_item, LiquidContainer):
            volume_to_empty = self._selected_bag_item.contained_volume
            self._selected_bag_item.decant(volume_to_empty)
        else:
            raise ValueError(f"Item {self._selected_bag_item.name} is not a LiquidContainer!")
        return True

    def _empty_from_ground_in_inventory_screen(self, _) -> bool:
        if isinstance(self._selected_ground_item, LiquidContainer):
            volume_to_empty = self._selected_ground_item.contained_volume
            self._selected_ground_item.decant(volume_to_empty)
        else:
            raise ValueError(f"Item {self._selected_ground_item.name} is not a LiquidContainer!")
        return True

    def _fill_from_bag_in_inventory_screen(self, _) -> bool:
        self._container_to_fill = self._selected_bag_item
        self.substate = Game.fill_container_substate
        return True

    def _fill_from_ground_in_inventory_screen(self, _) -> bool:
        self._container_to_fill = self._selected_ground_item
        self.substate = Game.fill_container_substate
        return True

    def _equip_for_slot_from_inventory_screen(self, _) -> bool:
        self._equipping_slot = list(self.character.equipped_items.keys())[self.selected_equipped_item_index]
        self.substate = Game.equip_for_substate
        return True

    def _unequip_from_inventory_screen(self, _) -> bool:
        item = self._selected_equipped_item
        for slot, i in self.character.equipped_items.items():
            if i is item:
                self.character.equipped_items[slot] = empty_space
                break
        if self.character.bag is not empty_space and self.character.bag.has_space():
            self.character.bag.add_item(item)
        else:
            if isinstance(self._ground_container, Tile):
                self._current_location.put_item(item, self._get_coords_of_creature(self.character))
            else:
                self._ground_container.add_item(item)
        return True

    def _consume_from_bag_in_inventory_screen(self, _) -> bool:
        self.character.apply_effects(self._selected_bag_item.effects)
        if isinstance(self._selected_bag_item, LiquidContainer):
            self._selected_bag_item.decant(1)
        else:
            self.character.bag.provide_item(self._selected_bag_item.weight,
                                            self._selected_bag_item, 1)
        return True

    def _consume_from_ground_in_inventory_screen(self, _) -> bool:
        self.character.apply_effects(self._selected_ground_item.effects)
        if isinstance(self._selected_ground_item, LiquidContainer):
            self._selected_ground_item.decant(1)
        else:
            self._ground_container.provide_item(self._selected_ground_item.weight,
                                                self._selected_ground_item, 1)
        return True

    def _character_rests(self, _) -> bool:
        self.character.rest()
        self._add_message('You rest for a bit.')
        self._living_world()
        return True

    def _drop_from_inventory_screen(self, _) -> bool:
        self.character.bag.remove_item(self._selected_bag_item)
        if isinstance(self._ground_container, Tile):
            self._current_location.put_item(self._selected_bag_item,
                                            self._get_coords_of_creature(self.character))
        else:
            self._ground_container.add_item(self._selected_bag_item)
        return True

    def _equip_from_bag_in_inventory_screen(self, _) -> bool:
        self.character.bag.remove_item(self._selected_bag_item)
        unequipped_item = self.character.swap_equipment(self._selected_bag_item)
        if unequipped_item is not empty_space:
            self.character.bag.add_item(unequipped_item)
        return True

    def _equip_from_ground_in_inventory_screen(self, _) -> bool:
        extra_load = self.character.weight_gained_by_swapping_equipment(self._selected_ground_item)
        available_load = self.character.max_load - self.character.load + extra_load
        item_to_equip = self._ground_container.provide_item(available_load,
                                                            self._selected_ground_item)
        dropped_item = self.character.swap_equipment(item_to_equip)
        if dropped_item is not empty_space:
            self._ground_container.add_item(dropped_item)
        return True

    def _stack_equip_from_bag_in_inventory_screen(self, _) -> bool:
        self.character.bag.remove_item(self._selected_bag_item)
        self.character.stack_equipment(self._selected_bag_item)
        return True

    def _stack_equip_from_ground_in_inventory_screen(self, _) -> bool:
        available_load = self.character.max_load - self.character.load
        item_to_equip = self._ground_container.provide_item(available_load,
                                                            self._selected_ground_item)
        self.character.stack_equipment(item_to_equip)
        return True

    def _pick_up_item(self, _) -> bool:
        available_load = self.character.max_load - self.character.load
        item_to_equip = self._ground_container.provide_item(available_load,
                                                            self._selected_ground_item)
        self.character.bag.add_item(item_to_equip)
        return True

    def _open_inventory(self, _) -> bool:
        self.substate = Game.inventory_substate
        self._ground_container = self._current_location.tile_at(self._get_coords_of_creature(self.character))
        return True

    def _back_to_scene(self, _) -> bool:
        self.substate = Game.scene_substate
        return True

    def _open_map(self, _) -> bool:
        self.substate = Game.map_substate
        return True

    def _character_moves(self, direction):
        self._move_character(direction)
        self._living_world()
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

    def _living_world(self) -> None:
        # TODO: Change effect visuals (blinking fires, etc)
        self._current_message = self._new_message
        self._new_message = ''
        self._turn += 1
        self._move_npcs()
        self.character.live()

    def sub_turn_tick(self) -> None:
        for position in list(self._sub_turn_effects):
            if position not in self._sub_turn_effects:
                continue
            effect = self._sub_turn_effects.pop(position)
            if position == effect['path'][-1]:
                next_position = position
            else:
                current_pos_index = effect['path'].index(position)
                next_position = effect['path'][current_pos_index + 1]
            if next_position in self._creature_coords:
                creature = self._creature_coords[next_position]
                creature.apply_effects(effect['effects'])
                self._end_effect(effect, next_position)
                if creature.is_dead:
                    self._creature_died(creature)
            elif next_position in self._sub_turn_effects:
                other_effect = self._sub_turn_effects.pop(next_position)
                for eff in [effect, other_effect]:
                    self._end_effect(eff, next_position)
            elif next_position == effect['path'][-1]:
                self._end_effect(effect, next_position)
            else:
                self._sub_turn_effects[next_position] = effect

    def _end_effect(self, effect: dict, position: tuple[int, int]) -> None:
        if 'item' in effect:
            self._current_location.put_item(effect['item'], position)

    def _creature_died(self, creature: Creature) -> None:
        coords = self._get_coords_of_creature(creature)
        for item in creature.get_drops():
            self._current_location.put_item(item, coords)
        self._creature_coords.pop(coords)
        for other_creature in self._creature_coords.values():
            if creature is other_creature.ranged_target:
                other_creature.ranged_target = None
        if creature is self._last_character_target:
            self._last_character_target = None

    def _add_message(self, message: str) -> None:
        self._new_message = message

    def _character_labor(self, direction: str) -> None:
        work_coords = calculate_new_position(self._get_coords_of_creature(self.character),
                                             direction, *self.world.size)
        if work_coords in self._creature_coords:
            self.substate = Game.scene_substate
            self._move_character(direction)
            return
        try:
            tile = self._current_location.tile_at(work_coords)
        except ValueError:
            self._add_message('You cannot work on that!')
            return
        drops, message = self.character.work_on(tile)
        if message:
            for drop in drops:
                self._current_location.put_item(drop, work_coords)
            self._add_message(message)
            self._last_character_target = None
        else:
            self._last_character_target = tile

    def _move_npcs(self):
        for old_coords in list(self._creature_coords.keys()):
            creature = self._creature_coords.get(old_coords)
            if creature is self.character or creature is None:
                continue
            if creature.is_dead:
                # This check is needed if an effect killed the creature already in _living_world()
                self._creature_died(creature)
                continue
            creature.live()
            goals = creature.get_goals()
            next_coords = self._current_location.get_goal_step(creature, old_coords,
                                                               goals, self._creature_coords)
            if next_coords in self._creature_coords:
                other_creature = self._creature_coords[next_coords]
                creature.bump_with(other_creature)
                if other_creature.is_dead:
                    self._creature_died(other_creature)
                if other_creature is self.character and self.substate == Game.working_substate:
                    self.substate = Game.scene_substate
            else:
                self._creature_coords.pop(old_coords)
                self._creature_coords[next_coords] = creature

    def _get_coords_of_creature(self, creature: Creature) -> tuple[int, int]:
        for coords in self._creature_coords:
            if self._creature_coords[coords] is creature:
                return coords
        raise ValueError(f'Creature {creature.name} cannot be found in coords dictionary!')

    def get_equipment_size(self) -> tuple[int, int]:
        return len(self.character.equipped_items), 1

    def get_equipment_data(self) -> str:
        lines = []
        for slot_name, item in self.character.effective_equipment.items():
            empty_label = dim(f'[{slot_name.lower()}]')
            label = item.name.capitalize() if item.name != config.empty_string else empty_label
            lines.append(f'{item.icon} {label}')
        return '\n'.join(lines)

    def get_available_substances(self) -> list[Union[LiquidContainer, SubstanceSource]]:
        tile_items = self._current_location.items_at(self._get_coords_of_creature(self.character))
        tile_terrain_substance = self._current_location.substance_at(self._get_coords_of_creature(self.character))
        bag_items = [] if self.character.bag is empty_space else self.character.bag.item_list
        compatible_substance_sources = []
        for item in tile_items + tile_terrain_substance + bag_items:
            if (isinstance(item, LiquidContainer) or isinstance(item, SubstanceSource)) \
                    and self._container_to_fill.can_hold(item.liquid) \
                    and item is not self._container_to_fill:
                compatible_substance_sources.append(item)
        return compatible_substance_sources

    def fill_container(self, source: Optional[LiquidContainer]) -> None:
        if source is not None:
            volume_to_fill = self._container_to_fill.empty_volume
            available_volume = source.contained_volume
            exchanged_volume = min(volume_to_fill, available_volume)
            self._container_to_fill.fill(source.liquid, exchanged_volume)
            source.decant(exchanged_volume)
        self.substate = Game.inventory_substate
        self._container_to_fill = None

    def get_available_equipment(self) -> list[GameObject]:
        all_ground_items = self._ground_container.item_list
        allowed_ground_items = [item for item in all_ground_items if self.character.can_carry_stack_or_item(item)]
        bag_items = [] if self.character.bag is empty_space else self.character.bag.item_list
        if self._equipping_slot is None:
            raise ValueError(f'Game _equipping_slot cannot be None while searching for equipment!')
        else:
            item_type = self.character.equipment_slots[self._equipping_slot]
        filtered_items = [item for item in allowed_ground_items + bag_items if isinstance(item, item_type)]
        return filtered_items

    def equip_item_from_selection_screen(self, item: Optional[Item]) -> None:
        if item is not None:
            if item in self._ground_container.item_list:
                container = self._ground_container
            else:
                container = self.character.bag
            available_load = self.character.max_load - self.character.load
            item_to_equip = container.provide_item(available_load, item)
            self.character.equipped_items[self._equipping_slot] = item_to_equip
        self.substate = Game.inventory_substate
        self._equipping_slot = None

    def set_active_container(self, container_name: str) -> None:
        self.active_inventory_container_name = container_name

    def get_bag_name(self) -> str:
        return '(no bag)' if self.character.bag is empty_space else f'Your {self.character.bag.name}'

    @staticmethod
    def get_ground_name() -> str:
        return config.ground

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
        item_details = self._selected_ground_item.details(weight_color=weight_color)
        tile_terrain_substance = self._current_location.substance_at(self._get_coords_of_creature(self.character))
        substance_details = [f"There is {sub.liquid.name} here!" for sub in tile_terrain_substance]
        return item_details + substance_details

    def get_bag_item_details(self, item_coords: tuple[int, int]) -> list[str]:
        try:
            self._selected_bag_item = self.character.bag.contents[item_coords[0]][item_coords[1]]
        except AttributeError:
            self._selected_bag_item = empty_space
        load_gauge = self._format_gauge(self.character.load, self.character.max_load, config.load_color)
        load_line = f'Load [{load_gauge}]'
        return self._selected_bag_item.details() + [load_line]

    def get_equipped_item_details(self, item_coords: tuple[int, int]) -> list[str]:
        self.selected_equipped_item_index = item_coords[0]
        effective_item = list(self.character.effective_equipment.values())[self.selected_equipped_item_index]
        return effective_item.details()

    def get_current_location_name(self) -> str:
        return self._current_location.name

    def get_character_hud(self) -> str:
        # TODO: Add active mode, current interaction target name and health/durability gauge (without
        #  numbers, also applicable to work-target terrains),
        #  target location (chosen on map, hinted with Travelling: West-NW)
        hp_gauge = self._format_gauge(self.character.hp, self.character.max_hp, config.hp_color)
        mana_gauge = self._format_gauge(self.character.mana, self.character.max_mana, config.mana_color)
        energy_gauge = self._format_gauge(self.character.energy, self.character.max_energy, config.energy_color,
                                          ailment_score=self.character.current_max_energy,
                                          ailment_color=config.famine_color)
        load_gauge = self._format_gauge(self.character.load, self.character.max_load, config.load_color)
        hud = f'HP [{hp_gauge}] | Mana [{mana_gauge}] | Energy [{energy_gauge}] | Load [{load_gauge}]\n'
        # Target and message line
        if self.substate == Game.looking_substate:
            message = self._current_location.tile_at(self._observed_target).description
            if self._observed_target in self._creature_coords:
                message += ' ' + self._creature_coords[self._observed_target].description
        elif self._current_message:
            message = self._current_message
        else:
            target_text = ''
            target_creature = self._last_character_target or self.character.ranged_target
            if isinstance(target_creature, (Creature, Tile)):
                target_hp_gauge = self._format_gauge(target_creature.hp,
                                                     target_creature.max_hp,
                                                     config.hp_color, show_numbers=False)
                target_text = f'Target: {target_creature.name} [{target_hp_gauge}]'
            statuses = '|'.join(self.character.get_statuses())
            inner_padding = ' ' * (config.location_width - raw_length(target_text) - raw_length(statuses))
            message = target_text + inner_padding + statuses
        hud += message
        return hud

    @staticmethod
    def _format_gauge(current_stat, max_stat, color, show_numbers: bool = True,
                      ailment_score: int = 0, ailment_color: str = console.fg.default) -> str:
        current_max = max_stat - ailment_score
        if show_numbers:
            raw_gauge = f'{current_stat}/{current_max}'.center(10, ' ')
        else:
            raw_gauge = ' ' * 10
        percentage_full = int((current_stat / max_stat) * 10)
        percentage_ailment = int((ailment_score / max_stat) * 10)
        percentage_empty = 10 - percentage_ailment - percentage_full
        colored_gauge = (color + raw_gauge[:percentage_full] + console.fx.end
                         + raw_gauge[percentage_full:percentage_full + percentage_empty]
                         + ailment_color + raw_gauge[percentage_full + percentage_empty:] + console.fx.end)
        return colored_gauge

    def _collate_creatures_and_effects(self) -> dict[tuple[int, int], GameObject]:
        effect_visuals = {pos: effect['item'] for pos, effect in self._sub_turn_effects.items()}
        combined_dict = {**self._creature_coords, **effect_visuals}
        return combined_dict

    def get_area_view(self) -> str:
        if self.substate == Game.looking_substate and self.character.ranged_target is not None:
            target_from = self._get_coords_of_creature(self.character)
            target_to = {v: k for k, v in self._creature_coords.items()}.get(self.character.ranged_target,
                                                                             self.character.ranged_target)
            return self._current_location.data_with_creatures(self._creature_coords,
                                                              target_from=target_from,
                                                              target_to=target_to)
        creatures_and_effects = self._collate_creatures_and_effects()
        return self._current_location.data_with_creatures(creatures_and_effects)

    def get_cursor_position_in_location(self) -> tuple[int, int]:
        if self.substate == Game.looking_substate:
            coords = self._observed_target
        else:
            coords = self._get_coords_of_creature(self.character)
        return coords[0] % config.location_height, coords[1] % config.location_width

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
        direction = self.character.confirm_movement_direction(direction)
        old_coords = self._get_coords_of_creature(self.character)
        new_coords = calculate_new_position(old_coords, direction, *self.world.size)
        old_location = self._current_location
        new_location = self.world.get_location(new_coords)
        if new_coords in self._creature_coords:
            self._last_character_target = self._creature_coords[new_coords]
            self.character.bump_with(self._last_character_target)
            if self._last_character_target.is_dead:
                self._creature_died(self._last_character_target)
        elif new_location.can_ocupy(self.character, new_coords):
            self._last_character_target = None
            self._creature_coords.pop(old_coords)
            self._creature_coords[new_coords] = self.character
            self._current_location = new_location
            if self._current_location is not old_location:
                old_location.stored_creatures = []
                for coords in list(self._creature_coords):
                    if self._creature_coords[coords] is not self.character:
                        old_location.stored_creatures.append(self._creature_coords.pop(coords))
                self.character.travel()
                self._creature_coords = self._current_location.load_creatures(self._creature_coords, self._turn)
        else:
            self._add_message("You can't go through that!")


class Terrain(GameObject):
    def __init__(self, passable: bool = True, exhaustion_factor: int = 0,
                 spawned_creatures: list[Species] = None,
                 substances: list[SubstanceSource] = None,
                 allowed_species: list[Species] = None,
                 **kwargs):
        super().__init__(**kwargs)
        self.passable = passable
        self.exhaustion_factor = exhaustion_factor
        self._allowed_species = allowed_species or []
        self.spawned_creatures: list[Species] = spawned_creatures or []
        self.substances = substances or []

    def is_passable_for(self, creature: Creature) -> bool:
        return self.passable or creature.species in self._allowed_species


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
grass = Terrain(color=console.fg.lightgreen, name='grass',
                description='Grass.', spawned_creatures=[field_mouse_species])
ashes = Terrain(color=console.fg.lightblack, name='ashes',
                description='Ashes.', spawned_creatures=[ash_beetle_species, rat_species])
dirt = Terrain(color=config.brown_fg_color, name='dirt',
               description='Dirt.', spawned_creatures=[field_mouse_species])
snow = Terrain(color=console.fg.white, name='snow',
               description='Snow.', spawned_creatures=[snow_hare_species])
sand = Terrain(color=console.fg.yellow, name='sand',
               description='Sand.', spawned_creatures=[sand_snake_species, scorpion_species])
ice = Terrain(color=console.fg.lightblue, name='ice',
              description='Slippery-looking ice.', spawned_creatures=[ice_mantis_species])
# Other base terrains
tree = Terrain(color=console.fg.lightgreen, name='tree', icon='T',
               description='A tree.', spawned_creatures=[fox_species, wolf_species])
dead_tree = Terrain(color=console.fg.lightblack, name='dead tree', icon='T',
                    description='A dead-looking tree.',
                    spawned_creatures=[wolf_species, swamp_dragon_species])
frozen_tree = Terrain(color=console.fg.lightblue, name='frozen tree', icon='T',
                      description='An ice-covered tree.',
                      spawned_creatures=[ice_fox_species, winter_wolf_species])
ice_block = Terrain(color=console.fg.lightblue, name='ice block', icon='%', passable=False,
                    description='A huge block of ice.',
                    spawned_creatures=[winter_wolf_species, ice_bear_species])
rocks = Terrain(color=console.fg.lightblack, name='rocks', icon='%', passable=False,
                description='A rock outcropping.',
                spawned_creatures=[bear_species, eagle_species], allowed_species=[gnome_race, eagle_species])
bush = Terrain(color=console.fg.lightgreen, name='bush', icon='#',
               description='A bush.', spawned_creatures=[fox_species])
swamp = Terrain(color=console.fg.lightgreen, name='swamp', icon='~',
                description='Swampy ground.',
                spawned_creatures=[crocodile_species, swamp_dragon_species, hydra_species])
salt_lake = Terrain(color=console.fg.lightyellow, name='salt lake',
                    description='Salt-encrusted water.', spawned_creatures=[crocodile_species])
jungle = Terrain(color=console.fg.green, name='tree', icon='T', passable=False,
                 description='Impenetrable jungle.',
                 spawned_creatures=[monkey_species, crocodile_species, jaguar_species])
all_base_terrains = [grass, ashes, dirt, snow, sand, ice, tree, dead_tree, frozen_tree, ice_block,
                     rocks, bush, swamp, salt_lake, jungle]
# Flavor terrains
poisonous_flowers = FlavorTerrain(color=console.fg.purple, name='poisonous flowers', icon='*',
                                  required_base_terrains=all_base_terrains, required_climates=ALL_CLIMATES)
bones = FlavorTerrain(color=console.fg.lightwhite, name='bones', icon='~',
                      description='Grizzly-looking bones.',
                      required_base_terrains=all_base_terrains, required_climates=ALL_CLIMATES)
venomous_thorns = FlavorTerrain(color=console.fg.lightgreen, name='venomous thorns', icon='#',
                                description='A bush.',
                                required_base_terrains=all_base_terrains, required_climates=ALL_CLIMATES)
junk_pile = FlavorTerrain(color=console.fg.lightblack, name='junk pile', icon='o',
                          description='Foul-smelling junk.',
                          required_base_terrains=all_base_terrains, required_climates=ALL_CLIMATES)
lava = FlavorTerrain(color=console.fg.red, name='lava', icon='~', passable=False,
                     description='A hole with bubbling lava!',
                     required_base_terrains=all_base_terrains, required_climates=[HOT_CLIMATE])
gold_vein = FlavorTerrain(color=console.fg.lightyellow, name='gold vein', icon='%', passable=False,
                          description='A rock outcropping.',
                          required_base_terrains=[rocks], required_climates=ALL_CLIMATES,
                          allowed_species=[gnome_race, eagle_species])
silver_vein = FlavorTerrain(color=console.fg.lightcyan, name='silver vein', icon='%', passable=False,
                            description='A rock outcropping.',
                            required_base_terrains=[rocks], required_climates=ALL_CLIMATES,
                            allowed_species=[gnome_race, eagle_species])
iron_vein = FlavorTerrain(color=console.fg.lightblue, name='iron vein', icon='%', passable=False,
                          description='A rock outcropping.',
                          required_base_terrains=[rocks], required_climates=ALL_CLIMATES,
                          allowed_species=[gnome_race, eagle_species])
mossy_rock = FlavorTerrain(color=console.fg.lightgreen, name='mossy rock', icon='%', passable=False,
                           description='A moss-covered boulder.',
                           required_base_terrains=all_base_terrains, required_climates=ALL_CLIMATES,
                           allowed_species=[gnome_race, eagle_species])
lichen_clump = FlavorTerrain(color=console.fg.lightgreen, name='lichen clump', icon='o',
                             description='A big clump of lichen.',
                             required_base_terrains=all_base_terrains, required_climates=[COLD_CLIMATE])
flowers = FlavorTerrain(color=console.fg.purple, name='flowers', icon='*',
                        description='A patch of flowers.',
                        required_base_terrains=all_base_terrains, required_climates=ALL_CLIMATES)
old_pavement = FlavorTerrain(color=console.fg.lightyellow, name='old pavement',
                             description='Old pavement.',
                             required_base_terrains=all_base_terrains, required_climates=ALL_CLIMATES)
ruined_wall = FlavorTerrain(color=config.brown_fg_color, name='ruined wall', icon='#', passable=False,
                            description='Ancient wall.',
                            required_base_terrains=all_base_terrains, required_climates=ALL_CLIMATES)
engraved_column = FlavorTerrain(color=config.brown_fg_color, name='engraved column', icon='|', passable=False,
                                description='An engraved column.',
                                required_base_terrains=all_base_terrains, required_climates=ALL_CLIMATES)
fireplace = FlavorTerrain(color=console.fg.lightyellow, name='fireplace', icon='o', passable=False,
                          description='A fireplace.',
                          required_base_terrains=all_base_terrains, required_climates=ALL_CLIMATES)
farmland = FlavorTerrain(color=console.fg.green + config.brown_bg_color, name='farmland', icon='=',
                         description='A tilled field.',
                         required_base_terrains=[grass, dirt, tree, jungle, bush, swamp],
                         required_climates=ALL_CLIMATES)
# Structure building blocks
poisoned_water = Terrain(color=console.fg.lightblack, name='poisoned water', icon='~', description='Murky water.')
water = Terrain(color=console.fg.blue, name='water', icon='~', description='Water.')
stilled_water = Terrain(color=console.fg.white, name='stilled water', icon='%', passable=False,
                        description='A column of stilled water.')
well_terrain = Terrain(color=console.fg.blue, icon='o', name='well', description='A water well.',
                       substances=[SubstanceSource(name='water well',
                                                   description='A water well.',
                                                   liquid=water_liquid)])

terrain_transformations = {
    rocks: {config.mining_skill: {'new_terrain': dirt, 'number_of_drops': 10,
                                  'drop_types': [Rock], 'drop_weights': [100],
                                  'message': 'You turn the boulder into rubble!'}},
    iron_vein: {config.mining_skill: {'new_terrain': dirt, 'number_of_drops': 10,
                                      'drop_types': [Rock, IronOre],
                                      'drop_weights': [75, 25],
                                      'message': 'You turn the boulder into rubble!'}},
    gold_vein: {config.mining_skill: {'new_terrain': dirt, 'number_of_drops': 10,
                                      'drop_types': [Rock, GoldOre],
                                      'drop_weights': [75, 25],
                                      'message': 'You turn the boulder into rubble!'}},
    silver_vein: {config.mining_skill: {'new_terrain': dirt, 'number_of_drops': 10,
                                        'drop_types': [Rock, SilverOre],
                                        'drop_weights': [75, 25],
                                        'message': 'You turn the boulder into rubble!'}},
    ice_block: {config.mining_skill: {'new_terrain': ice, 'number_of_drops': 10,
                                      'drop_types': [IceShard], 'drop_weights': [100],
                                      'message': 'The ice breaks into razor-sharp pieces!'}},
    stilled_water: {config.mining_skill: {'new_terrain': water, 'number_of_drops': 10,
                                          'drop_types': [StilledWaterShard], 'drop_weights': [100],
                                          'message': 'The translucent column breaks apart!'}},
    bones: {config.scavenging_skill: {'new_terrain': bones, 'number_of_drops': 3,
                                      'drop_types': [None, JunkItem], 'drop_weights': [80, 20],
                                      'message': 'You sift through the pile of bones.'}},
    junk_pile: {config.scavenging_skill: {'new_terrain': junk_pile, 'number_of_drops': 3,
                                          'drop_types': [None, JunkItem], 'drop_weights': [40, 60],
                                          'message': 'You sift through the pile of bones.'}}
}


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
                  CHAOS_FORCE: [sand, rocks, salt_lake],
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
        self._transformations = {}
        self._last_skill_applied: Optional[str] = None

    @property
    def name(self):
        return self.terrain.name

    @property
    def hp(self) -> int:
        return 100 - self._transformations.get(self._last_skill_applied, 0)

    @property
    def max_hp(self) -> int:
        return 100

    def apply_skill(self, skill: str, strength: int) -> tuple[list[Item], str]:
        self._last_skill_applied = skill
        self._transformations[skill] = self._transformations.get(skill, 0) + strength
        if self._transformations[skill] >= 100:
            return self._apply_transformation(skill)
        return [], ''

    def _apply_transformation(self, skill: str) -> tuple[list[Item], str]:
        transformation_result = terrain_transformations[self.terrain][skill]
        self.terrain = transformation_result['new_terrain']
        drops = []
        for x in range(transformation_result['number_of_drops']):
            item_type = random.choices(transformation_result['drop_types'],
                                       transformation_result['drop_weights'])[0]
            if item_type is not None:
                drops.append(item_type())
        self._transformations = {}
        return drops, transformation_result['message']

    @property
    def applicable_skills(self) -> list[str]:
        return list(terrain_transformations.get(self.terrain, []))

    @property
    def description(self):
        description = self.terrain.description
        if self.item_list:
            description += ' There are items here.'
        return description

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
        return len(self.item_list) < self._height * self._width

    @property
    def terrain_substances(self) -> list[SubstanceSource]:
        return self.terrain.substances


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
        self._last_spawn_time = -1 * config.random_creatures_respawn_period
        self.stored_creatures: list[Creature] = []
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
        self._local_name = None if self._structure is None else self._structure.name
        if self._local_name:
            name = ', '.join([self._local_name, self._region_name])
        else:
            name = self._region_name
        super().__init__(height=config.location_height, width=config.location_width,
                         icon=visual.raw_icon, color=visual.color, name=name)
        self._contents: list[list[Tile]] = []

    def get_empty_spot_for(self, creature: Creature) -> tuple[int, int]:
        for row in range(self._height):
            for column in range(self._width):
                coords = (row + self._top_left[0], column + self._top_left[1])
                if self.tile_at(coords).is_passable_for(creature):
                    return coords

    def get_goal_step(self, creature: Creature, current_coords: tuple[int, int],
                      goals: list[str], other_creatures: dict[tuple[int, int], Creature]) -> tuple[int, int]:
        for goal in goals:
            if goal is config.chase_humanoid_behavior:
                step = self._find_prey(current_coords, other_creatures=other_creatures, hunter=creature)
                if step == current_coords:
                    continue
                else:
                    return step
            if goal is config.run_from_humanoid_behavior:
                step = self._run_from_humanoids(current_coords, other_creatures=other_creatures, runner=creature)
                if step == current_coords:
                    continue
                else:
                    return step
            elif goal is config.random_behavior:
                return self._choose_random_passable_neighbor(creature, current_coords)
            else:
                raise ValueError(f'Unhandled behaviour: "{goal}" of creature "{creature.name}"!')

    def _run_from_humanoids(self, coords: tuple[int, int],
                            other_creatures: dict[tuple[int, int], Creature],
                            runner: Creature) -> tuple[int, int]:
        distance = runner.perception_radius
        for hunter_coords, hunter in other_creatures.items():
            if isinstance(hunter.species, HumanoidSpecies) and coord_distance(coords, hunter_coords) <= distance:
                good_y_direction = [1, -1][hunter_coords[0] > coords[0]]
                good_x_direction = [1, -1][hunter_coords[1] > coords[1]]
                safe_steps = [(coords[0] + good_y_direction, coords[1] + good_x_direction),
                              (coords[0], coords[1] + good_x_direction),
                              (coords[0] + good_y_direction, coords[1])
                              ]
                for step in safe_steps:
                    try:
                        if self.tile_at(step).is_passable_for(runner):
                            return step
                    except ValueError:
                        pass
        return coords

    def _find_prey(self, coords,
                   other_creatures: dict[tuple[int, int], Creature],
                   hunter: Creature) -> tuple[int, int]:
        distance = hunter.perception_radius
        for prey_coords, prey in other_creatures.items():
            if isinstance(prey.species, HumanoidSpecies) and coord_distance(coords, prey_coords) < distance:
                path = direct_path(coords, prey_coords)
                if self.tile_at(path[1]).is_passable_for(hunter):
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

    def load_creatures(self, local_creatures: dict[tuple[int, int], Creature],
                       current_turn: int) -> dict[tuple[int, int], Creature]:
        # TODO: Get respawning creatures from the flavor/structure
        # TODO: Get non-respawning creatures from the structure
        if current_turn - self._last_spawn_time < config.random_creatures_respawn_period:
            additional_creatures = self.stored_creatures[:]
        else:
            additional_creatures = []
            self._last_spawn_time = current_turn
            species_lists = [t.spawned_creatures for t in self._terrains]
            weights = self._terrain_weights[:]
            for creature_count in range(int(sum(weights) // 20)):
                species_list = random.choices(species_lists, weights=weights)[0]
                if not species_list:
                    continue
                if len(species_list) > len(config.creature_rarity_scale):
                    raise ValueError(f'Creature rarity scale is not long enough for'
                                     f' list of length {len(species_list)}!')
                chosen_weights = config.creature_rarity_scale[:len(species_list)]
                chosen_creature_species = random.choices(species_list, chosen_weights)[0]
                additional_creatures.append(Animal(chosen_creature_species))
        for creature_instance in additional_creatures:
            new_coords = self._random_coords()
            while new_coords in local_creatures or not self.can_ocupy(creature_instance, new_coords):
                new_coords = self._random_coords()
            local_creatures[new_coords] = creature_instance
        return local_creatures

    def _random_coords(self):
        return random.randint(self._top_left[0], self._top_left[0] + self._height - 1), \
            random.randint(self._top_left[1], self._top_left[1] + self._width - 1)

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
        if not self.contains_coords(coords):
            raise ValueError(f'Bad coordinates {coords} for Location tile!')
        new_coords = self._local_coords(coords)
        return self.contents[new_coords[0]][new_coords[1]]

    def contains_coords(self, coords: tuple[int, int]) -> bool:
        local_coords = self._local_coords(coords)
        return 0 <= local_coords[0] < config.location_height and 0 <= local_coords[1] < config.location_width

    def _local_coords(self, coords: tuple[int, int]) -> tuple[int, int]:
        return coords[0] - self._top_left[0], coords[1] - self._top_left[1]

    def data_with_creatures(self, creatures: dict[tuple[int, int], GameObject] = None,
                            target_from: tuple[int, int] = None,
                            target_to: tuple[int, int] = None) -> str:
        rows = [[c.icon for c in row]
                for row in self.contents]
        for coords, creature in creatures.items():
            local_coords = self._local_coords(coords)
            rows[local_coords[0]][local_coords[1]] = creature.icon
        if target_from and target_to:
            path = direct_path(target_from, target_to)[1:]
            for coords in path:
                icon = config.target_cross_icon if coords == path[-1] else config.target_path_icon
                local_coords = self._local_coords(coords)
                rows[local_coords[0]][local_coords[1]] = icon
        rows = [''.join(row) for row in rows]
        return '\n'.join(rows)

    def items_at(self, coords: tuple[int, int]) -> list[Item]:
        return self.tile_at(coords).item_list

    def substance_at(self, coords: tuple[int, int]) -> list[SubstanceSource]:
        return self.tile_at(coords).terrain_substances

    def put_item(self, item: Item, coords: tuple[int, int]) -> None:
        tile = self.tile_at(coords)
        if tile.has_space():
            tile.add_item(item)
        else:
            tile_list = [coords]
            current_index = 0
            while True:
                neighbors = []
                while current_index < len(tile_list):
                    neighbors += self._all_neighbors(tile_list[current_index])
                    current_index += 1
                new_neighbors = list(set(neighbors) - set(tile_list))
                for neighbor in new_neighbors:
                    new_tile = self.tile_at(neighbor)
                    if new_tile.has_space():
                        new_tile.add_item(item)
                        return
                    else:
                        tile_list.append(neighbor)
                if not new_neighbors:
                    break
            raise NotImplementedError(f'Implement Overflow achievement here!')

    def remove_item(self, item: Item, coords: tuple[int, int]) -> None:
        self.tile_at(coords).remove_item(item)


# TODO: PoI selection and randomization
# TODO: Init the locations with the PoI/force/base terrains (handles gradients)
class Region(Container):
    height_in_tiles = config.region_size * config.location_height
    width_in_tiles = config.region_size * config.location_width
    region_names = {COLD_CLIMATE: {snow: 'Frost lands',
                                   frozen_tree: 'Frozen glade',
                                   tree: 'Winter woods',
                                   ice: 'Ice fields',
                                   ice_block: 'Glacier',
                                   rocks: 'Snowy peaks'},
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
                                  salt_lake: 'Chott',
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


class World(Container):
    region_suffixes = {CHAOS_FORCE: """of Blood
of Blisters
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
of the Tyrant
of Vampires 
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
    bag = LiquidContainer(max_volume=3, name='empty bag/bag of {}')
    assert isinstance(bag, LiquidContainer)
    assert bag.name == 'empty bag'
    bag.fill(water_liquid, 30)
    assert bag.name == 'bag of water'
    assert isinstance(bag, Liquid)
