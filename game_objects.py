from typing import Optional, Type, Union
import random
import console
import config
from utils import make_stats, add_dicts


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
    def icon(self) -> str:
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


class Effect(GameObject):
    def __init__(self, color_range: list[str] = None, duration: int = 0, tile: 'Tile' = None,
                 is_observable: bool = False, **kwargs):
        if duration <= 0:
            raise ValueError(f"Effect {self.name} cannot have a duration <= 0!")
        if tile is None:
            raise ValueError(f"Effect {self.name} cannot have None as a tile!")
        super().__init__(**kwargs)
        self.is_observable = is_observable
        self._color_range = color_range or [self.color]
        self._tile = tile
        self.color = self._color_range[0]
        self._duration = duration

    def tick(self, creature: 'Creature' = None) -> None:
        self.duration -= 1
        self.color = random.choice(self._color_range)
        self._tick_specific_effects(creature)

    @property
    def duration(self) -> int:
        return self._duration

    @duration.setter
    def duration(self, value) -> None:
        self._duration = value
        self._effects_on_duration_change()

    def _tick_specific_effects(self, creature: 'Creature' = None) -> None:
        raise NotImplementedError(f"Effect {self.name} must implement _tick_specific_effects!")

    def _effects_on_duration_change(self) -> None:
        raise NotImplementedError(f"Effect {self.name} must implement _effects_on_duration_change!")


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
    def item_list(self) -> list['Item']:
        full_list = []
        for line in self._contents:
            full_list += line
        return full_list


class Item(GameObject):
    def __init__(self, weight: int = 0, effects: dict = None,
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
    def effects(self) -> dict:
        return self._effects


class Immobile:
    """A mixin class marking objects that cannot be picked up"""
    pass


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


class Resource(Item):
    """An abstract class for singleton object instances to be used as resources in the game"""

    @property
    def name(self) -> str:
        return self.color + self._name + console.fx.end


class Liquid(Resource):
    """A container class for singleton object instances to be used as liquids in the game"""
    pass


class Power(Resource):
    """A container class for singleton object instances to be used as power in the game"""
    pass


class LiquidContainer(Item):
    """An object facilitating interactions with Liquid instances"""

    def __init__(self, max_volume: int = 0, **kwargs):
        super().__init__(**kwargs)
        self._max_volume: int = max_volume
        self.liquid: Union[Liquid, Item] = empty_space
        self.contained_amount: int = 0
        if '/' not in kwargs.get('name', '') or '{' not in kwargs.get('name', ''):
            raise ValueError("LiquidContainer name must support splitting and formatting!")

    @property
    def name(self) -> str:
        if self.liquid is empty_space:
            return self._name.split('/')[0]
        else:
            return self._name.split('/')[1].format(self.liquid.name)

    @property
    def description(self) -> str:
        if self.liquid is empty_space:
            return f"It can hold {self.empty_volume} units of liquid."
        else:
            return f"It holds {self.contained_amount} units of {self.liquid.name}," \
                   f" can hold {self.empty_volume} more."

    @property
    def effects(self) -> dict[str, int]:
        return self.liquid.effects

    @property
    def weight(self):
        return self._own_weight + self.liquid.weight * self.contained_amount

    @property
    def __class__(self) -> Type:
        if self.liquid is empty_space:
            return LiquidContainer
        else:
            return self.liquid.__class__

    @property
    def empty_volume(self) -> int:
        empty_volume = self._max_volume - self.contained_amount
        if empty_volume < 0:
            raise ValueError(f"Container {self.name} is holding more than the max_volume!")
        return empty_volume

    def can_hold(self, substance: Item) -> bool:
        return isinstance(substance, Liquid) and \
            (self.liquid is empty_space or self.liquid is substance)

    def fill(self, liquid: Liquid, volume: int) -> None:
        """Fills the container and returns the remainder amount to update the other container"""
        if self.liquid is not empty_space and liquid is not self.liquid:
            raise ValueError("Container cannot hold more than one Liquid!")
        if volume < 1:
            raise ValueError(f"Container cannot be filled with {volume} volume of {liquid.name}!")
        if self.liquid is empty_space:
            self.liquid = liquid
        if volume > self.empty_volume:
            raise ValueError(f"Container {self.name} cannot exceed max volume!")
        self.contained_amount += volume

    def decant(self, volume_to_decant) -> None:
        if volume_to_decant > self.contained_amount:
            raise ValueError(f"Container {self.name} asked to decant {volume_to_decant},"
                             f" but {self.contained_amount} available!")
        self.contained_amount -= volume_to_decant
        if self.contained_amount == 0:
            self.liquid = empty_space


class ResourceSource(Item, Immobile):
    """An abstract class representing natural sources that provide a Resource without acting as containers"""
    def __init__(self, resource: Resource = None,
                 contained_amount: int = 9999, **kwargs):
        super().__init__(color=resource.color, **kwargs)
        if resource is None:
            raise ValueError(f"Source of type {self.__class__} cannot be initialized without a resource!")
        self.resource = resource
        self.contained_amount = contained_amount


class LiquidSource(ResourceSource):
    """
    A natural source of a Liquid
    Examples: a well, a river, a lava lake
    """
    def __init__(self, resource: Liquid = None, name: str = "(liquid source)",
                 description: str = '(empty liquid source description)'):
        super().__init__(resource, name=name, icon='o', description=description)
        self.liquid = resource

    def decant(self, volume_to_decant) -> None:
        return

    @property
    def name(self) -> str:
        return self.resource.color + self._name + console.fx.end


class PowerSource(ResourceSource):
    """
    A natural source of Power
    Examples: fires, magical lay lines
    """
    def __init__(self, resource: Power = None, name: str = "(power source)",
                 description: str = '(empty power source description)', **kwargs):
        if '{' not in name:
            raise ValueError(f"PowerResource name must support formatting, but got '{name}'!")
        super().__init__(resource, name=name, icon='*', description=description, **kwargs)

    @property
    def name(self) -> str:
        if self.contained_amount < 15:
            strength = 'weak'
        elif self.contained_amount < 30:
            strength = 'medium'
        else:
            strength = 'strong'
        name = self._name.format(strength)
        return self.resource.color + name + console.fx.end


class Helmet(Item):
    pass


class Armor(Item):
    def __init__(self, armor_skill: str, armor_stat: str, combat_exhaustion: int, **kwargs):
        super().__init__(**kwargs)
        self.armor_skill = armor_skill
        self.armor_stat = armor_stat
        self.combat_exhaustion = combat_exhaustion


class Back(PhysicalContainer):
    """Includes cloaks and backpacks"""
    pass


class Boots(Item):
    pass


class MainHand:
    pass


class Weapon(Item):
    def __init__(self, melee_weapon_skill: str = config.improvised_combat_skill,
                 melee_weapon_stat: str = config.Str,
                 combat_exhaustion: int = None, **kwargs):
        super().__init__(**kwargs)
        self.melee_weapon_skill = melee_weapon_skill
        self.melee_weapon_stat = melee_weapon_stat
        self.combat_exhaustion = combat_exhaustion or self.weight
        if config.melee_combat not in self.effects.get(config.combat_effects, {}):
            raise ValueError(f"Item {self.name} must have a combat/melee effect dictionary!")


class LargeWeapon(Weapon, MainHand):
    pass


class RangedWeapon(Weapon, MainHand):
    def __init__(self, ranged_weapon_type: str, ranged_weapon_skill: str,
                 ranged_weapon_stat: str, max_distance: int, **kwargs):
        super().__init__(**kwargs)
        self.ranged_weapon_type = ranged_weapon_type
        self.max_distance = max_distance
        self.ranged_weapon_skill = ranged_weapon_skill
        self.ranged_weapon_stat = ranged_weapon_stat
        if config.ranged_combat not in self.effects.get(config.combat_effects, {}):
            raise ValueError(f"Item {self.name} must have a combat/ranged effect dictionary!")

    def can_shoot(self, ammo: Optional[Item]) -> bool:
        return isinstance(ammo, RangedAmmo) and ammo.ranged_ammo_type == self.ranged_weapon_type


class Tool(Weapon, MainHand):
    def __init__(self, work_skill: str, work_stat: str, work_exhaustion: int = None, **kwargs):
        super().__init__(**kwargs)
        self.work_skill = work_skill
        self.work_exhaustion = work_exhaustion or self.weight
        self.work_stat = work_stat


class Offhand:
    pass


class Shield(Item, Offhand):
    def __init__(self, combat_exhaustion: int, **kwargs):
        super().__init__(**kwargs)
        self.shield_skill = config.shield_skill
        self.shield_stat = config.End
        self.combat_exhaustion = combat_exhaustion


class RangedAmmo(Item, Offhand):
    def __init__(self, ranged_ammo_type: str, **kwargs):
        super().__init__(**kwargs)
        self.ranged_ammo_type = ranged_ammo_type
        if config.ranged_combat not in self.effects.get(config.combat_effects, {}):
            raise ValueError(f"Item {self.name} must have a combat/ranged effect dictionary!")


class ThrownWeapon(RangedWeapon, RangedAmmo):
    pass


class SmallWeapon(Weapon, MainHand, Offhand):
    pass


class TwoHandedWeapon(Weapon, MainHand):
    pass


class AnimalWeapon(Weapon):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.combat_exhaustion = 1
        self.melee_weapon_skill = config.animal_innate_weapon_skill
        self.melee_weapon_stat = config.Str


class AnimalArmor(Item):
    pass


class EdibleAnimalPart(Item):
    pass


base_sentient_equipment_slots = {config.head_slot: Helmet, config.armor_slot: Armor,
                                 config.main_hand_slot: MainHand, config.offhand_slot: Offhand,
                                 config.back_slot: Back, config.boots_slot: Boots}
base_animal_equipment_slots = {config.animal_weapon_slot: AnimalWeapon,
                               config.animal_armor_slot: AnimalArmor,
                               config.animal_meat_slot: EdibleAnimalPart}
sentient_races = []


class Species(GameObject):

    initial_equipment = ()

    def __init__(self, ai: dict[str, list[str]] = config.basic_ai,
                 initial_disposition: str = config.indifferent_disposition,
                 base_effect_modifiers: dict[str, int] = None,
                 base_resistances_and_affinities: dict[str, int] = None,
                 active_effects: dict[str, int] = None,
                 consumable_types: list[Type[Item]] = None,
                 base_skills: dict[str, int] = None,
                 active_phase: str = config.daylight_phase,
                 **kwargs):
        super().__init__(**kwargs)
        self.initial_disposition = initial_disposition
        self.active_phase = active_phase
        self.ai = ai
        self.base_skills = base_skills or {}
        self.base_effect_modifiers = base_effect_modifiers or {}
        self.base_resistances_and_affinities = base_resistances_and_affinities or {}
        self.active_effects = {config.non_rest_energy_regen_effect: 1}
        if active_effects is not None:
            self.active_effects.update(active_effects)
        if consumable_types is None:
            self.consumable_types = [EdibleAnimalPart, Liquid]
        else:
            self.consumable_types = consumable_types
        self.equipment_slots = {}

    @property
    def base_stats(self) -> dict[str, int]:
        raise NotImplementedError(f'Class {self.__class__} must implement base stats!')


class HumanoidSpecies(Species):
    @property
    def base_stats(self) -> dict[str, int]:
        return make_stats(default=5)

    def __init__(self, fist_weapon: Type[Item], clothes: Type[Item], **kwargs):
        super().__init__(**kwargs)
        self.fist_weapon: Item = fist_weapon()
        self.clothes: Item = clothes()
        sentient_races.append(self)
        self.equipment_slots = base_sentient_equipment_slots.copy()


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
        self.equipment_slots = base_animal_equipment_slots.copy()
        self.base_skills[config.animal_innate_weapon_skill] = int(self._base_stats[config.Dex]
                                                                  / config.max_stat_value
                                                                  * config.max_skill_value)
        

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
        self.active_phase = self.species.active_phase
        if self.description == config.empty_string:
            self._description = self.species.description
        self._disposition = self.species.initial_disposition
        self._ai = self.species.ai
        self._skills = self.species.base_skills.copy()
        self.stats = self.species.base_stats.copy()
        self._effect_modifiers = self.species.base_effect_modifiers
        self._resistances_and_affinities = self.species.base_resistances_and_affinities
        self._active_effects: dict[str, int] = self.species.active_effects
        self.equipment_slots = self.species.equipment_slots
        self.equipped_items = {k: empty_space for k in self.equipment_slots}
        for item_type in self.species.initial_equipment:
            self.swap_equipment(item_type())
        self._hp = self.max_hp
        self._mana = self.max_mana
        self._energy = self.max_energy
        self._hunger: int = 0
        self._thirst: int = 0
        self._sustenance_needs: int = 0
        self._age: int = 0
        self.ranged_target: Optional[Union[Creature, tuple[int, int]]] = None
        self.is_detected: bool = True

    @property
    def effective_equipment(self) -> dict:
        return self.equipped_items

    @property
    def perception_radius(self) -> int:
        return int(self.stats[config.Per])

    @property
    def load(self) -> int:
        return sum([item.weight for item in self.equipped_items.values()])

    @property
    def _combat_exhaustion(self) -> int:
        exhaustion = 0
        for item in set(self.effective_equipment.values()):
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
        self._energy = min(self.max_energy - self.unusable_energy, max(0, value))

    def _get_hungry(self, change):
        """Add hunger and thirst on every 100 points of energy spent or every 100 turns"""
        self._sustenance_needs += change
        if self._sustenance_needs >= 100:
            famine = self._sustenance_needs // 100
            self.hunger += famine
            self.thirst += famine
            self._sustenance_needs = self._sustenance_needs % 100
            self._energy = min(self.max_energy - self.unusable_energy, self._energy)

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
        modifier = self._get_effect_modifier(config.max_hp_modifier)
        return int(base_hp * modifier)

    @property
    def max_mana(self) -> int:
        base_mana = self.stats[config.Wil] * 10
        modifier = self._get_effect_modifier(config.max_mana_modifier)
        return int(base_mana * modifier)

    @property
    def max_energy(self) -> int:
        base_energy = int(self.stats[config.End] * 10)
        modifier = self._get_effect_modifier(config.max_energy_modifier)
        return int(base_energy * modifier)

    @property
    def unusable_energy(self) -> int:
        sustenance_modifier = (self.hunger + self.thirst) // 10 * 10
        return self.max_energy * sustenance_modifier // 100

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

    @property
    def _evasion_ability(self) -> int:
        raise NotImplementedError(f"Class {self.__class__} must implement _evasion_ability!")

    def _react_to_hit(self) -> None:
        raise NotImplementedError(f"Class {self.__class__} must implement _react_to_hit!")

    def apply_effects(self, effects: dict[str, int]) -> None:
        """
        Personalized effect values are created through effect modifiers, resistances,
        and affinities that depend on the race and the actions of the character.
        """
        # We make a copy so that the effects are not modified for other creatures they apply to
        local_effects = effects.copy()
        if config.dodge_difficulty in local_effects:
            dodge = self._evasion_ability
            difficulty = local_effects[config.dodge_difficulty]
            if random.random() < dodge / (dodge + difficulty) * config.max_dodge_chance:
                return
            else:
                local_effects.pop(config.dodge_difficulty)
                self._react_to_hit()
        for name, effect_size in local_effects.items():
            final_effect_size = self.get_final_effect_size(name, effect_size)
            self._apply_effect(name, final_effect_size)

    def get_final_effect_size(self, effect_name: str, effect_size: int) -> int:
        modified_effect_size = int(effect_size * self._get_effect_modifier(effect_name))
        final_effect_size = modified_effect_size + self._get_effect_resistance_or_affinity(effect_name)
        return final_effect_size

    def _get_effect_resistance_or_affinity(self, effect_name: str) -> int:
        effect_adjustment = self._resistances_and_affinities.get(effect_name, 0)
        for item in set(self.effective_equipment.values()):
            effective_value = item.effects.get(config.resistances_and_affinities, {}).get(effect_name, 0)
            if isinstance(item, Armor) and effect_name != item.armor_skill and effective_value != 0:
                skill = self._effective_skill(item.armor_skill) / config.max_skill_value
                effective_value = int(effective_value * (0.5 + 0.5 * skill))
            elif isinstance(item, Shield) and effect_name != item.shield_skill and effective_value != 0:
                skill = self._effective_skill(item.shield_skill) / config.max_skill_value
                effective_value = int(effective_value * (0.5 + 0.5 * skill))
            elif isinstance(item, (LargeWeapon, SmallWeapon, TwoHandedWeapon)) \
                    and effect_name != item.melee_weapon_skill and effective_value != 0 \
                    and not effect_name.startswith(config.terrain_passage_cost):
                skill = self._effective_skill(item.melee_weapon_skill) / config.max_skill_value
                effective_value = int(effective_value * (0.5 + 0.5 * skill))
            effect_adjustment += effective_value
        return effect_adjustment

    def _get_effect_modifier(self, effect_name: str) -> float:
        effect_value = self._effect_modifiers.get(effect_name, 1)
        for item in set(self.effective_equipment.values()):
            effect_adjustment = item.effects.get(config.effect_modifiers, {}).get(effect_name, 1)
            if isinstance(item, Armor) and effect_name != item.armor_skill and effect_adjustment != 1:
                skill = self._effective_skill(item.armor_skill) / config.max_skill_value
                effect_adjustment = 1 + (effect_adjustment - 1) * (0.5 + 0.5 * skill)
            elif isinstance(item, Shield) and effect_name != item.shield_skill and effect_adjustment != 1:
                skill = self._effective_skill(item.shield_skill) / config.max_skill_value
                effect_adjustment = 1 + (effect_adjustment - 1) * (0.5 + 0.5 * skill)
            elif isinstance(item, (LargeWeapon, SmallWeapon, TwoHandedWeapon)) \
                    and effect_name != item.melee_weapon_skill and effect_adjustment != 1 \
                    and not effect_name.startswith(config.terrain_passage_cost):
                skill = self._effective_skill(item.melee_weapon_skill) / config.max_skill_value
                effect_adjustment = 1 + (effect_adjustment - 1) * (0.5 + 0.5 * skill)
            effect_value *= effect_adjustment
        return effect_value

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
        elif name.startswith(config.damage_effect_prefix):
            self.hp -= effect_size
        elif name.startswith(config.terrain_passage_cost):
            self.energy -= effect_size
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
        load_modifier = self._get_effect_modifier(config.max_load_modifier)
        return int(base_load * load_modifier)

    def can_equip(self, item: Item) -> bool:
        return any([isinstance(item, slot_type) for slot_type in self.equipment_slots.values()])

    def can_carry(self, item: Item) -> bool:
        return item.weight <= self.max_load - self.load

    def can_carry_stack_or_item(self, item: Item) -> bool:
        if isinstance(item, Immobile):
            return False
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
                if isinstance(item, TwoHandedWeapon):
                    load_difference -= self.equipped_items[config.offhand_slot].weight
                elif isinstance(item, Offhand) \
                        and isinstance(self.equipped_items[config.main_hand_slot], TwoHandedWeapon):
                    load_difference -= self.equipped_items[config.main_hand_slot].weight
                return available_load >= load_difference
        return False

    def weight_gained_by_swapping_equipment(self, item: Item) -> int:
        for slot, slot_type in self.equipment_slots.items():
            if isinstance(item, slot_type):
                weight_gained = self.equipped_items[slot].weight
                if isinstance(item, TwoHandedWeapon):
                    weight_gained += self.equipped_items[config.offhand_slot].weight
                elif isinstance(item, Offhand) \
                        and isinstance(self.equipped_items[config.main_hand_slot], TwoHandedWeapon):
                    weight_gained += self.equipped_items[config.main_hand_slot].weight
                return weight_gained
        raise TypeError(f"Item {item.name} cannot be equipped in any slot!")

    def swap_equipment(self, item: Item) -> list[Item]:
        removed_items = []
        for slot, slot_type in self.equipment_slots.items():
            if isinstance(item, slot_type):
                removed_items.append(self.equipped_items[slot])
                self.equipped_items[slot] = item
                if isinstance(item, TwoHandedWeapon):
                    removed_items.append(self.equipped_items[config.offhand_slot])
                    self.equipped_items[config.offhand_slot] = empty_space
                elif isinstance(item, Offhand) \
                        and isinstance(self.equipped_items[config.main_hand_slot], TwoHandedWeapon):
                    removed_items.append(self.equipped_items[config.main_hand_slot])
                    self.equipped_items[config.main_hand_slot] = empty_space
                return removed_items

    def get_goals(self) -> list[str]:
        return self._ai[self._disposition]

    def get_drops(self):
        return [item for item in self.equipped_items.values() if item is not empty_space]

    def melee_with(self, enemy: 'Creature', weapon: Weapon) -> None:
        skill = self._effective_skill(weapon.melee_weapon_skill)
        hit_effects = {config.dodge_difficulty: skill}
        skill_ratio = skill / config.max_skill_value
        for effect, effect_size in weapon.effects[config.combat_effects][config.melee_combat].items():
            if effect == config.physical_damage:
                effective_damage = int(effect_size * (0.75 + 0.75 * skill_ratio)
                                       + self.stats[weapon.melee_weapon_stat] / 4 * self._exhaustion_modifier)
                hit_effects[effect] = effective_damage
            else:
                hit_effects[effect] = effect_size
        enemy.apply_effects(hit_effects)

    def _post_melee_effects(self, weapon: Weapon) -> None:
        raise NotImplementedError(f"Class {self.__class__} must implement _post_melee_effects!")

    def _get_weapons(self) -> list[Weapon]:
        raise NotImplementedError(f"Class {self.__class__} must implement _get_weapons!")

    def bump_with(self, other_creature: 'Creature') -> None:
        if self._disposition == config.aggressive_disposition or self.raw_icon == '@':
            for weapon in self._get_weapons():
                self.melee_with(other_creature, weapon)
                self._post_melee_effects(weapon)
            self.energy -= self._combat_exhaustion

    def rest(self):
        self.energy += random.randint(1, max(int(self.stats[config.End] / 5), 1))
        if random.random() < (self.stats[config.End] / config.max_stat_value / 2) * (self.energy / self.max_energy):
            self.hp += 1

    @property
    def is_dead(self) -> bool:
        return self.hp <= 0

    def get_stats_data(self) -> dict[str, str]:
        return {stat: f'{value:.2f}' for stat, value in self.stats.items()}

    def get_modifier_data(self) -> dict[str, str]:
        modifiers = set(self._effect_modifiers.keys())
        for item in set(self.effective_equipment.values()):
            modifiers = modifiers | set(item.effects.get(config.effect_modifiers, {}).keys())
        modifier_data = {}
        for modifier in modifiers:
            clean_name = modifier.split(config.skill_delimiter)[-1]
            value = self._get_effect_modifier(modifier)
            modifier_data[clean_name] = f'x {value:.2f}'
        return modifier_data

    def get_resistances_and_affinities_data(self) -> dict[str, str]:
        modifiers = set(self._resistances_and_affinities.keys())
        for item in set(self.effective_equipment.values()):
            modifiers = modifiers | set(item.effects.get(config.resistances_and_affinities, {}).keys())
        modifier_data = {}
        for modifier in modifiers:
            clean_name = modifier.split(config.skill_delimiter)[-1]
            value = self._get_effect_resistance_or_affinity(modifier)
            modifier_data[clean_name] = f'{value}'
        return modifier_data

    def get_secondary_stats_data(self) -> dict[str, str]:
        return {'Hp': f'{self.hp}/{self.max_hp}',
                'Mana': f'{self.mana}/{self.max_mana}',
                'Energy': f'{self.energy}/{self.max_energy}',
                'Load': f'{self.load}/{self.max_load}',
                'Dodge': f'{self._evasion_ability}'
                }

    def _effective_skill(self, skill_name: str) -> int:
        raw_skill = self._skills.get(skill_name, 0)
        modifier = self._get_effect_modifier(skill_name)
        return int(raw_skill * modifier)

    def can_traverse(self, tile: 'Tile') -> str:
        cost_type, passage_cost = list(tile.effects[config.terrain_passage_cost].items())[0]
        final_cost = self.get_final_effect_size(cost_type, passage_cost)
        if self.max_energy < final_cost:
            return 'You cannot go there!'
        if self.energy < final_cost:
            return 'You are too tired to move forward!'
        return ''

    def traverse(self, tile: 'Tile') -> None:
        self.apply_effects(tile.effects[config.terrain_passage_cost])

    def get_skills_data(self) -> dict[str, int]:
        return {skill: self._effective_skill(skill) for skill in self._skills}


class Animal(Creature):
    def __init__(self, species: AnimalSpecies, **kwargs):
        super().__init__(species, **kwargs)

    @property
    def _evasion_ability(self) -> int:
        dex_modifier = self.stats[config.Dex] / config.max_stat_value
        evasion_skill = dex_modifier * self._exhaustion_modifier * config.max_skill_value
        return int(evasion_skill)

    def _react_to_hit(self) -> None:
        return

    def _post_melee_effects(self, weapon: Weapon) -> None:
        return

    def _get_weapons(self) -> list[Weapon]:
        return [self.equipped_items[config.animal_weapon_slot]]


class Humanoid(Creature):
    def __init__(self, species: HumanoidSpecies, **kwargs):
        super().__init__(species, **kwargs)
        self.species = species

    @property
    def bag(self):
        return self.equipped_items[config.back_slot]

    @property
    def available_tools(self) -> list[str]:
        tools = []
        bag_items = [] if self.bag is empty_space else self.bag.item_list
        for item in bag_items + list(self.effective_equipment.values()):
            tag = item.effects.get(config.tool_tag, '')
            if tag:
                tools.append(tag)
        return tools

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
        elif isinstance(effective_items[config.main_hand_slot], TwoHandedWeapon):
            effective_items[config.offhand_slot] = effective_items[config.main_hand_slot]
        if effective_items[config.armor_slot] is empty_space:
            effective_items[config.armor_slot] = self.species.clothes
        return effective_items

    @property
    def effective_equipped_items(self) -> dict:
        effective_items = {**self.equipped_items}
        if isinstance(effective_items[config.main_hand_slot], TwoHandedWeapon):
            effective_items[config.offhand_slot] = effective_items[config.main_hand_slot]
        return effective_items

    @property
    def _combat_exhaustion(self) -> int:
        exhaustion = 0
        for item in set(self.effective_equipment.values()):
            if hasattr(item, 'combat_exhaustion'):
                if isinstance(item, Armor):
                    skill_mod = self._effective_skill(item.armor_skill) / config.max_skill_value
                    exhaustion += item.combat_exhaustion * (1 - 0.5 * skill_mod)
                elif isinstance(item, Shield):
                    skill_mod = self._effective_skill(item.shield_skill) / config.max_skill_value
                    exhaustion += item.combat_exhaustion * (1 - 0.5 * skill_mod)
                elif isinstance(item, (LargeWeapon, SmallWeapon, TwoHandedWeapon)):
                    skill_mod = self._effective_skill(item.melee_weapon_skill) / config.max_skill_value
                    exhaustion += item.combat_exhaustion * (1 - 0.5 * skill_mod)
                else:
                    exhaustion += item.combat_exhaustion
        return int(exhaustion)

    def _get_weapons(self) -> list[Weapon]:
        used_weapons = [self.effective_equipment[config.main_hand_slot]]
        if isinstance(self.effective_equipment[config.offhand_slot], Weapon) \
                and random.random() < self.stats[config.Dex] / config.max_stat_value:
            used_weapons.append(self.effective_equipment[config.offhand_slot])
        return used_weapons

    def _get_armor(self) -> Armor:
        return self.effective_equipment[config.armor_slot]

    def _get_shield(self) -> Optional[Shield]:
        offhand = self.effective_equipment[config.offhand_slot]
        if isinstance(offhand, Shield):
            return offhand
        return

    def _post_melee_effects(self, weapon: Weapon) -> None:
        self._improve(weapon.melee_weapon_skill, weapon.melee_weapon_stat)

    @property
    def _evasion_ability(self) -> int:
        load_modifier = 1 - self.load / self.max_load
        dex_modifier = self.stats[config.Dex] / config.max_stat_value
        evasion_modifier = self._get_effect_modifier(config.evasion_modifier)
        all_mods = dex_modifier * load_modifier * evasion_modifier * self._exhaustion_modifier
        return int(all_mods * config.max_skill_value)

    def _react_to_hit(self) -> None:
        armor = self._get_armor()
        self._improve(armor.armor_skill, armor.armor_stat)
        shield = self._get_shield()
        if shield is not None:
            self._improve(shield.shield_skill, shield.shield_stat)

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

    def shoot(self) -> tuple[RangedAmmo, int, dict[str, int]]:
        weapon = self._get_ranged_weapon()
        ammo = self._get_ranged_ammo()
        if weapon is ammo:
            effects = weapon.effects[config.combat_effects][config.ranged_combat].copy()
        else:
            effects = add_dicts(weapon.effects[config.combat_effects][config.ranged_combat],
                                ammo.effects[config.combat_effects][config.ranged_combat])
        if config.physical_damage in effects:
            effects[config.physical_damage] += int(self.stats[weapon.ranged_weapon_stat] / 5)
        current_skill = self._effective_skill(weapon.ranged_weapon_skill)
        self._improve(weapon.ranged_weapon_skill, weapon.ranged_weapon_stat)
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
            self._skills[skill_name] = current_skill + 1
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
            if isinstance(item, Tool) and item.work_skill in tile.applicable_skills:
                if item.work_exhaustion > self.energy:
                    return [], "You are too tired to work!"
                current_skill = self._effective_skill(item.work_skill)
                skill_strength = int(self.stats[item.work_stat] + current_skill / 10)
                self.energy -= item.work_exhaustion
                self._improve(item.work_skill, item.work_stat)
                result = tile.apply_skill(item.work_skill, strength=skill_strength)
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


class Terrain(Item):
    def __init__(self,
                 spawned_creatures: list[Species] = None,
                 substances: list[LiquidSource] = None,
                 effects: dict = None,
                 **kwargs):
        if effects is None:
            effects = {}
        if config.terrain_passage_cost not in effects:
            effects[config.terrain_passage_cost] = {config.terrain_passage_cost: 0}
        super().__init__(effects=effects, **kwargs)
        self.spawned_creatures: list[Species] = spawned_creatures or []
        self.substances = substances or []
        self.transformations = {}


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


class Tile(PhysicalContainer):
    def __init__(self, terrain: Terrain):
        super().__init__(height=config.tile_size, width=config.tile_size)
        self.terrain = terrain
        for source in self.terrain.substances:
            self.add_item(source)
        self._transformations = {}
        self._last_skill_applied: Optional[str] = None

    @property
    def name(self):
        return self.terrain.name

    @property
    def effects(self) -> dict:
        return self.terrain.effects

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
        transformation_result = self.terrain.transformations[skill]
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
        return list(self.terrain.transformations)

    @property
    def description(self):
        description = self.terrain.description
        if self.item_list:
            description += ' There are items here.'
        return description

    @property
    def icon(self) -> str:
        item_list = self.item_list
        if len(item_list) == 1:
            return item_list[0].icon
        elif len(item_list) > 1:
            return config.multiple_items_icon
        return self.terrain.icon
