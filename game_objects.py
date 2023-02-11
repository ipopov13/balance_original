from typing import Optional, Type, Union
import random
import console
import config
from utils import make_stats


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


class Helmet(Item):
    pass


class Armor(Item):
    def __init__(self, armor: int, armor_skill: str, armor_stat: str,
                 evasion_modifier: float, combat_exhaustion: int, **kwargs):
        super().__init__(**kwargs)
        self.armor = armor
        self.armor_skill = armor_skill
        self.armor_stat = armor_stat
        self.evasion_modifier = evasion_modifier
        self.combat_exhaustion = combat_exhaustion


class Back(PhysicalContainer):
    """Includes cloaks and backpacks"""
    pass


class Boots(Item):
    pass


class MainHand(Item):
    def __init__(self, melee_damage: int = 0, melee_weapon_skill: str = config.improvised_combat_skill,
                 melee_weapon_stat: str = config.Str,
                 combat_exhaustion: int = None, **kwargs):
        super().__init__(**kwargs)
        self.melee_damage = melee_damage
        self.melee_weapon_skill = melee_weapon_skill
        self.melee_weapon_stat = melee_weapon_stat
        self.combat_exhaustion = combat_exhaustion or self.weight


class RangedWeapon(MainHand):
    def __init__(self, ranged_weapon_type: str, ranged_weapon_skill: str,
                 ranged_weapon_stat: str, max_distance: int,
                 ranged_damage: int, **kwargs):
        super().__init__(**kwargs)
        self.ranged_weapon_type = ranged_weapon_type
        self.max_distance = max_distance
        self.ranged_weapon_skill = ranged_weapon_skill
        self.ranged_weapon_stat = ranged_weapon_stat
        self.ranged_damage = ranged_damage

    def can_shoot(self, ammo: Optional[Item]) -> bool:
        return isinstance(ammo, RangedAmmo) and ammo.ranged_ammo_type == self.ranged_weapon_type


class Tool(MainHand):
    def __init__(self, work_skill: str, work_stat: str, work_exhaustion: int = None, **kwargs):
        super().__init__(**kwargs)
        self.work_skill = work_skill
        self.work_exhaustion = work_exhaustion or self.weight
        self.work_stat = work_stat


class Offhand(Item):
    pass


class Shield(Offhand):
    def __init__(self, evasion_modifier: float, combat_exhaustion: int, **kwargs):
        super().__init__(**kwargs)
        self.shield_skill = config.shield_skill
        self.shield_stat = config.End
        self.combat_exhaustion = combat_exhaustion
        self.evasion_modifier = evasion_modifier


class RangedAmmo(Offhand):
    def __init__(self, ranged_ammo_type: str, ranged_damage: int = 0, **kwargs):
        super().__init__(**kwargs)
        self.ranged_ammo_type = ranged_ammo_type
        self.ranged_damage = ranged_damage


class ThrownWeapon(RangedWeapon, RangedAmmo):
    pass


class TwoHandedWeapon(MainHand):
    pass


class AnimalWeapon(Item):
    def __init__(self, melee_damage: int, **kwargs):
        super().__init__(**kwargs)
        self.combat_exhaustion = 1
        self.melee_damage = melee_damage


class AnimalArmor(Item):
    def __init__(self, armor: int, **kwargs):
        super().__init__(**kwargs)
        self.armor = armor


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

    def __init__(self, custom_ai: dict[str, list[str]] = None,
                 initial_disposition: str = config.indifferent_disposition,
                 base_effect_modifiers: dict[str, int] = None,
                 active_effects: dict[str, int] = None,
                 consumable_types: list[Type[Item]] = None,
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
        self.base_effect_modifiers = base_effect_modifiers or {}
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
        return int(self.stats[config.Per])

    @property
    def load(self) -> int:
        return sum([item.weight for item in self.equipped_items.values()])

    @property
    def melee_damage(self) -> int:
        raise NotImplementedError(f"Class {self.__class__} must implement melee_damage!")

    @property
    def armor(self) -> int:
        skill = self._armor_skill / config.max_skill_value
        effective_armor = int(self.equipment_armor() * (0.5 + 0.5 * skill))
        return effective_armor

    @property
    def _armor_skill(self) -> int:
        raise NotImplementedError(f"Class {self.__class__} must implement _armor_skill!")

    def equipment_armor(self) -> int:
        armor = 0
        for item in set(self.effective_equipment.values()):
            try:
                armor += item.armor
            except AttributeError:
                pass
        return armor

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
        return int(self.stats[config.End] * 10)

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

    @property
    def _evasion_ability(self) -> float:
        raise NotImplementedError(f"Class {self.__class__} must implement _evasion_ability!")

    def _effects_at_dodge_attempt(self) -> None:
        raise NotImplementedError(f"Class {self.__class__} must implement _effects_at_dodge_attempt!")

    def apply_effects(self, effects: dict[str, int]) -> None:
        """
        Personalized effect values are created through the _effect_modifiers dictionary that
        depends on the race and the actions of the character.
        """
        if config.dodge_difficulty in effects:
            dodge = self._evasion_ability
            difficulty = effects[config.dodge_difficulty]
            self._effects_at_dodge_attempt()
            if random.random() < dodge / (dodge + difficulty) * config.max_dodge_chance:
                return
            else:
                effects.pop(config.dodge_difficulty)
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

    def melee_with(self, enemy: 'Creature') -> None:
        self.energy -= self._combat_exhaustion
        hit_effects = {config.dodge_difficulty: self._melee_skill,
                       config.normal_damage_effect: self.melee_damage}
        enemy.apply_effects(hit_effects)

    @property
    def _melee_skill(self) -> int:
        raise NotImplementedError(f"Class {self.__class__} must implement _melee_skill!")

    def bump_with(self, other_creature: 'Creature') -> None:
        if self._disposition == config.aggressive_disposition or self.raw_icon == '@':
            self.melee_with(other_creature)

    def _receive_normal_damage(self, damage: int) -> None:
        self.hp -= max(0, damage - self.armor)

    def rest(self):
        self.energy += random.randint(1, max(int(self.stats[config.End] / 5), 1))
        if random.random() < (self.stats[config.End] / config.max_stat_value / 2) * (self.energy / self.max_energy):
            self.hp += 1

    @property
    def is_dead(self) -> bool:
        return self.hp <= 0

    def get_stats_data(self) -> dict[str, str]:
        return {stat: f'{value:.2f}' for stat, value in self.stats.items()}

    def get_secondary_stats_data(self) -> dict[str, str]:
        return {'Hp': f'{self.hp}/{self.max_hp}',
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

    @property
    def melee_damage(self) -> int:
        weapon_damage = 0
        for item in set(self.effective_equipment.values()):
            try:
                weapon_damage += item.melee_damage
            except AttributeError:
                pass
        stat_damage = int(random.randint(1, max(int(self.stats[config.Str] / 4), 1)) * self._exhaustion_modifier)
        return stat_damage + weapon_damage

    @property
    def _melee_skill(self) -> int:
        return int((self.stats[config.Dex] / config.max_stat_value)
                   * config.max_skill_value
                   * self._exhaustion_modifier)

    @property
    def _evasion_ability(self) -> float:
        return (self.stats[config.Dex] / config.max_stat_value) * self._exhaustion_modifier

    def _effects_at_dodge_attempt(self) -> None:
        return

    @property
    def _armor_skill(self) -> int:
        return 100


class Humanoid(Creature):
    def __init__(self, species: HumanoidSpecies, **kwargs):
        super().__init__(species, **kwargs)
        self.species = species

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
                else:
                    exhaustion += item.combat_exhaustion
        return int(exhaustion)

    def _get_main_hand(self) -> MainHand:
        return self.effective_equipment[config.main_hand_slot]

    def _get_armor(self) -> Armor:
        return self.effective_equipment[config.armor_slot]

    def _get_shield(self) -> Optional[Shield]:
        offhand = self.effective_equipment[config.offhand_slot]
        if isinstance(offhand, Shield):
            return offhand
        return

    def melee_with(self, enemy: 'Creature') -> None:
        super().melee_with(enemy)
        weapon = self._get_main_hand()
        self._improve(weapon.melee_weapon_skill, weapon.melee_weapon_stat)

    @property
    def _melee_skill(self) -> int:
        weapon = self._get_main_hand()
        return self._effective_skill(weapon.melee_weapon_skill)

    @property
    def _armor_skill(self) -> int:
        armor = self._get_armor()
        return self._effective_skill(armor.armor_skill)

    @property
    def _evasion_ability(self) -> float:
        evasion_skill = self._effective_skill(config.evasion_skill)
        armor = self._get_armor()
        shield = self._get_shield()
        shield_modifier = 1
        if shield is not None:
            shield_skill = self._effective_skill(config.shield_skill) / config.max_skill_value
            shield_modifier = 1 + (shield.evasion_modifier - 1) * (0.5 + 0.5 * shield_skill)
        return evasion_skill * armor.evasion_modifier * shield_modifier

    def _effects_at_dodge_attempt(self) -> None:
        self._improve(config.evasion_skill, config.Dex)

    @property
    def melee_damage(self) -> int:
        weapon = self._get_main_hand()
        skill = self._effective_skill(weapon.melee_weapon_skill) / config.max_skill_value
        effective_weapon_damage = (weapon.melee_damage * (0.75 + 0.75 * skill)
                                   + self.stats[weapon.melee_weapon_stat] / 4 * self._exhaustion_modifier)
        return int(effective_weapon_damage)

    def _receive_normal_damage(self, damage: int) -> None:
        super()._receive_normal_damage(damage)
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

    @property
    def _ranged_damage(self) -> int:
        ranged_weapon = self._get_ranged_weapon()
        ammo = self._get_ranged_ammo()
        if ranged_weapon is ammo:
            weapon_damage = ranged_weapon.ranged_damage
        else:
            weapon_damage = ranged_weapon.ranged_damage + ammo.ranged_damage
        stats = int((self.stats[config.Dex] + self.stats[config.Per]) / 4)
        return random.randint(0, max(stats, 1)) + weapon_damage

    def shoot(self) -> tuple[RangedAmmo, int, dict[str, int]]:
        weapon = self._get_ranged_weapon()
        ammo = self._get_ranged_ammo()
        effects = {config.normal_damage_effect: self._ranged_damage}
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
        self.transformations = {}

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
    def icon(self):
        item_list = self.item_list
        if len(item_list) == 1:
            return item_list[0].icon
        elif len(item_list) > 1:
            return config.multiple_items_icon
        return self.terrain.icon

    def is_passable_for(self, creature: Creature):
        return self.terrain.is_passable_for(creature)

    def has_space(self):
        return len(self.item_list) < self._height * self._width

    @property
    def terrain_substances(self) -> list[SubstanceSource]:
        return self.terrain.substances
