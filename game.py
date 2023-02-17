from typing import Optional, Union
import console
import random
from utils import coord_distance, calculate_new_position, dim, direct_path, raw_length
import game_objects as go
from world import Location, World
import commands
import config
import items
import effects


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
    races = go.sentient_races

    def __init__(self):
        self._turn = 0
        self.character: Optional[go.Humanoid] = None
        self._current_location: Optional[Location] = None
        self.character_name: Optional[str] = None
        self._last_character_target = None
        self._equipping_slot: Optional[str] = None
        self._selected_ground_item: go.Item = go.empty_space
        self._selected_bag_item: go.Item = go.empty_space
        self.selected_equipped_item_index: int = 0
        self._ground_container: Optional[go.PhysicalContainer] = None
        self._container_to_fill: Optional[go.LiquidContainer] = None
        self.active_inventory_container_name = self.get_ground_name()
        self._creature_coords: dict[tuple[int, int], go.Creature] = {}
        self.World: Optional[World] = None
        self.state: str = Game.welcome_state
        self.substate: Optional[str] = None
        self._new_message: str = ''
        self._current_message: str = ''
        self._observed_target: Optional[tuple[int, int]] = None
        self._turn_effects: dict[tuple[int, int], go.Effect] = {}
        self._sub_turn_effects: dict = {}
        self._chosen_transformation: Optional[dict[str, int]] = None

    @property
    def _selected_equipped_item(self):
        return list(self.character.effective_equipped_items.values())[self.selected_equipped_item_index]

    def start_game(self, character_race) -> None:
        if character_race is None:
            return
        self.character = go.Humanoid(name=self.character_name, species=character_race,
                                     description='You are standing here.', color=console.fg.default,
                                     icon='@')
        # TODO: This is the initial testing configuration. Add the selected starting location here.
        initial_coords = (0, 0)
        self._current_location = self.World.get_location(initial_coords)
        character_coords = self._current_location.get_empty_spot_for(self.character)
        self._creature_coords[character_coords] = self.character
        self._creature_coords = self._current_location.load_creatures(self._creature_coords, self._turn)

        self._current_location.put_item(items.Bag(), character_coords)
        self._current_location.put_item(items.ShortSword(color=console.fg.red), character_coords)
        water_skin = items.WaterSkin()
        water_skin.fill(items.water_liquid, 2)
        self._current_location.put_item(water_skin, character_coords)
        self._current_location.put_item(items.Firewood(), character_coords)
        self._current_location.put_item(items.Firewood(), character_coords)
        self._current_location.put_item(items.Firewood(), character_coords)
        self._current_location.put_item(items.AcornGun(), character_coords)
        for i in range(10):
            self._current_location.put_item(items.Acorn(), character_coords)
        self._current_location.put_item(items.FlintAndSteel(), character_coords)
        self._current_location.put_item(items.PlateArmor(), character_coords)

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
                if self._item_can_be_transformed(self._selected_ground_item):
                    transformation = self._get_item_transformation(self._selected_ground_item)
                    self._chosen_transformation = transformation[config.transformation_effects]
                    inventory_commands[transformation[config.transformation_command]()] = self._transform_ground_item
                if self.character.bag is not go.empty_space \
                        and self.character.bag.has_space() \
                        and self.character.can_carry_stack_or_item(self._selected_ground_item) \
                        and self._selected_ground_item is not go.empty_space:
                    inventory_commands[commands.InventoryPickUp()] = self._pick_up_item
                if self.character.can_stack_equipment(self._selected_ground_item) \
                        and self.character.can_carry_stack_or_item(self._selected_ground_item):
                    inventory_commands[commands.InventoryEquip()] = self._stack_equip_from_ground_in_inventory_screen
                elif self.character.can_swap_equipment(self._selected_ground_item):
                    inventory_commands[commands.InventoryEquip()] = self._equip_from_ground_in_inventory_screen
                if self.character.can_consume(self._selected_ground_item):
                    inventory_commands[commands.InventoryConsume()] = self._consume_from_ground_in_inventory_screen
                if isinstance(self._selected_ground_item, go.LiquidContainer) \
                        and self._selected_ground_item.empty_volume > 0:
                    inventory_commands[commands.InventoryFill()] = self._fill_from_ground_in_inventory_screen
                if isinstance(self._selected_ground_item, go.LiquidContainer) \
                        and self._selected_ground_item.contained_volume > 0:
                    inventory_commands[commands.InventoryEmpty()] = self._empty_from_ground_in_inventory_screen
            # "From bag" commands
            if self.active_inventory_container_name == self.get_bag_name():
                if self._item_can_be_transformed(self._selected_bag_item):
                    transformation = self._get_item_transformation(self._selected_bag_item)
                    self._chosen_transformation = transformation[config.transformation_effects]
                    inventory_commands[transformation[config.transformation_command]()] = self._transform_bag_item
                if self._selected_bag_item is not go.empty_space \
                        and (self._ground_container.has_space()
                             or isinstance(self._ground_container, go.Tile)):
                    inventory_commands[commands.InventoryDrop()] = self._drop_from_inventory_screen
                if self.character.can_stack_equipment(self._selected_bag_item):
                    inventory_commands[commands.InventoryEquip()] = self._stack_equip_from_bag_in_inventory_screen
                elif self.character.can_equip(self._selected_bag_item):
                    inventory_commands[commands.InventoryEquip()] = self._equip_from_bag_in_inventory_screen
                if self.character.can_consume(self._selected_bag_item):
                    inventory_commands[commands.InventoryConsume()] = self._consume_from_bag_in_inventory_screen
                if isinstance(self._selected_bag_item, go.LiquidContainer) \
                        and self._selected_bag_item.empty_volume > 0:
                    inventory_commands[commands.InventoryFill()] = self._fill_from_bag_in_inventory_screen
                if isinstance(self._selected_bag_item, go.LiquidContainer) \
                        and self._selected_bag_item.contained_volume > 0:
                    inventory_commands[commands.InventoryEmpty()] = self._empty_from_bag_in_inventory_screen
            # "From equipment" commands
            if self.active_inventory_container_name == config.equipment_title:
                if self._selected_equipped_item is not go.empty_space \
                        and ((self.character.bag is not go.empty_space and self.character.bag.has_space())
                             or (self._ground_container.has_space()
                                 or isinstance(self._ground_container, go.Tile))):
                    inventory_commands[commands.InventoryUnequip()] = self._unequip_from_inventory_screen
                if self._selected_equipped_item is go.empty_space:
                    inventory_commands[commands.InventoryEquipSlot()] = self._equip_for_slot_from_inventory_screen
            return inventory_commands
        else:
            return {}

    def _transform_ground_item(self, _) -> bool:
        self._ground_container.provide_item(self._selected_ground_item.weight,
                                            self._selected_ground_item, 1)
        for effect, effect_size in self._chosen_transformation.items():
            self._apply_effect(effect, effect_size, self._get_coords_of_creature(self.character))
        self._chosen_transformation = None
        return True

    def _transform_bag_item(self, _) -> bool:
        self.character.bag.provide_item(self._selected_bag_item.weight,
                                        self._selected_bag_item, 1)
        for effect, effect_size in self._chosen_transformation.items():
            self._apply_effect(effect, effect_size, self._get_coords_of_creature(self.character))
        self._chosen_transformation = None
        return True

    def _apply_effect(self, effect: str, effect_size: int, coords: tuple[int, int]) -> None:
        if effect == config.light_a_fire:
            if isinstance(self._turn_effects.get(coords), effects.Campfire):
                self._turn_effects[coords].length += effect_size
            else:
                self._turn_effects[coords] = effects.Campfire(effect_size)

    def _item_can_be_transformed(self, item: go.Item):
        available_tools = self.character.available_tools
        return any([tool in available_tools
                    for tool in items.item_transformations.get(item.__class__, {})])

    def _get_item_transformation(self, item: go.Item) -> dict:
        available_tools = self.character.available_tools
        for tool, transformation in items.item_transformations[item.__class__].items():
            if tool in available_tools:
                return transformation
        raise IndexError(f"No tool available for transforming {item.name}!")

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
                if isinstance(target, go.Creature):
                    target = self._get_coords_of_creature(target)
                character_position = self._get_coords_of_creature(self.character)
                distance = coord_distance(character_position, target)
                max_distance = self.character.get_shooting_range()
                if distance > max_distance:
                    self._add_message("The target is beyond your weapon's range!")
                else:
                    projectile, skill, effect_dict = self.character.shoot()
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
                                         'effects': effect_dict}
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
        new_coords = calculate_new_position(self._observed_target, direction, *self.World.size)
        if self.World.get_location(new_coords) is not self._current_location:
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
        if isinstance(self._selected_bag_item, go.LiquidContainer):
            volume_to_empty = self._selected_bag_item.contained_volume
            self._selected_bag_item.decant(volume_to_empty)
        else:
            raise ValueError(f"Item {self._selected_bag_item.name} is not a LiquidContainer!")
        return True

    def _empty_from_ground_in_inventory_screen(self, _) -> bool:
        if isinstance(self._selected_ground_item, go.LiquidContainer):
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
                self.character.equipped_items[slot] = go.empty_space
                break
        if self.character.bag is not go.empty_space and self.character.bag.has_space():
            self.character.bag.add_item(item)
        else:
            if isinstance(self._ground_container, go.Tile):
                self._current_location.put_item(item, self._get_coords_of_creature(self.character))
            else:
                self._ground_container.add_item(item)
        return True

    def _consume_from_bag_in_inventory_screen(self, _) -> bool:
        self.character.apply_effects(self._selected_bag_item.effects.get(config.consumable_effects, {}))
        if isinstance(self._selected_bag_item, go.LiquidContainer):
            self._selected_bag_item.decant(1)
        else:
            self.character.bag.provide_item(self._selected_bag_item.weight,
                                            self._selected_bag_item, 1)
        return True

    def _consume_from_ground_in_inventory_screen(self, _) -> bool:
        self.character.apply_effects(self._selected_ground_item.effects.get(config.consumable_effects, {}))
        if isinstance(self._selected_ground_item, go.LiquidContainer):
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
        if isinstance(self._ground_container, go.Tile):
            self._current_location.put_item(self._selected_bag_item,
                                            self._get_coords_of_creature(self.character))
        else:
            self._ground_container.add_item(self._selected_bag_item)
        return True

    def _equip_from_bag_in_inventory_screen(self, _) -> bool:
        self.character.bag.remove_item(self._selected_bag_item)
        unequipped_items = self.character.swap_equipment(self._selected_bag_item)
        for unequipped_item in unequipped_items:
            if unequipped_item is not go.empty_space and self.character.bag.has_space():
                self.character.bag.add_item(unequipped_item)
            elif unequipped_item is not go.empty_space:
                self._current_location.put_item(unequipped_item,
                                                self._get_coords_of_creature(self.character))
        return True

    def _equip_from_ground_in_inventory_screen(self, _) -> bool:
        extra_load = self.character.weight_gained_by_swapping_equipment(self._selected_ground_item)
        available_load = self.character.max_load - self.character.load + extra_load
        item_to_equip = self._ground_container.provide_item(available_load,
                                                            self._selected_ground_item)
        dropped_items = self.character.swap_equipment(item_to_equip)
        for dropped_item in dropped_items:
            if dropped_item is not go.empty_space:
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
        self.World = World()
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
        self._current_message = self._new_message
        self._new_message = ''
        self._turn += 1
        self._move_npcs()
        self.character.live()
        for position in list(self._turn_effects):
            effect = self._turn_effects[position]
            effect.tick()
            if effect.length == 0:
                self._turn_effects.pop(position)

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

    def _creature_died(self, creature: go.Creature) -> None:
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
                                             direction, *self.World.size)
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

    def _get_coords_of_creature(self, creature: go.Creature) -> tuple[int, int]:
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

    def get_available_substances(self) -> list[Union[go.LiquidContainer, go.SubstanceSource]]:
        tile_items = self._current_location.items_at(self._get_coords_of_creature(self.character))
        tile_terrain_substance = self._current_location.substance_at(self._get_coords_of_creature(self.character))
        bag_items = [] if self.character.bag is go.empty_space else self.character.bag.item_list
        compatible_substance_sources = []
        for item in tile_items + tile_terrain_substance + bag_items:
            if (isinstance(item, go.LiquidContainer) or isinstance(item, go.SubstanceSource)) \
                    and self._container_to_fill.can_hold(item.liquid) \
                    and item is not self._container_to_fill:
                compatible_substance_sources.append(item)
        return compatible_substance_sources

    def fill_container(self, source: Optional[go.LiquidContainer]) -> None:
        if source is not None:
            volume_to_fill = self._container_to_fill.empty_volume
            available_volume = source.contained_volume
            exchanged_volume = min(volume_to_fill, available_volume)
            self._container_to_fill.fill(source.liquid, exchanged_volume)
            source.decant(exchanged_volume)
        self.substate = Game.inventory_substate
        self._container_to_fill = None

    def get_available_equipment(self) -> list[go.GameObject]:
        all_ground_items = self._ground_container.item_list
        allowed_ground_items = [item for item in all_ground_items if self.character.can_carry_stack_or_item(item)]
        bag_items = [] if self.character.bag is go.empty_space else self.character.bag.item_list
        if self._equipping_slot is None:
            raise ValueError(f'Game _equipping_slot cannot be None while searching for equipment!')
        else:
            item_type = self.character.equipment_slots[self._equipping_slot]
        filtered_items = [item for item in allowed_ground_items + bag_items if isinstance(item, item_type)]
        if self._equipping_slot == config.main_hand_slot \
                and self.character.equipped_items[config.offhand_slot] is not go.empty_space:
            filtered_items = [item for item in filtered_items if not isinstance(item, go.TwoHandedWeapon)]
        return filtered_items

    def equip_item_from_selection_screen(self, item: Optional[go.Item]) -> None:
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
        return '(no bag)' if self.character.bag is go.empty_space else f'Your {self.character.bag.name}'

    @staticmethod
    def get_ground_name() -> str:
        return config.ground

    def get_ground_items(self) -> str:
        return self._current_location.get_items_data_at(self._get_coords_of_creature(self.character))

    def get_bag_items(self) -> str:
        return '' if self.character.bag is go.empty_space else self.character.bag.data()

    def get_bag_size(self) -> tuple[int, int]:
        return (0, 0) if self.character.bag is go.empty_space else self.character.bag.size

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
            self._selected_bag_item = go.empty_space
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
        # TODO: Add target location (chosen on map, hinted with Travelling: West-NW)
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
            if self._observed_target in self._turn_effects:
                message += ' ' + self._turn_effects[self._observed_target].description
        elif self._current_message:
            message = self._current_message
        else:
            target_text = ''
            target_creature = self._last_character_target or self.character.ranged_target
            if isinstance(target_creature, (go.Creature, go.Tile)):
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

    def _collate_creatures_and_effects(self) -> dict[tuple[int, int], go.GameObject]:
        sub_turn_effect_visuals = {pos: effect['item'] for pos, effect in self._sub_turn_effects.items()}
        combined_dict = {**self._turn_effects, **self._creature_coords, **sub_turn_effect_visuals}
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
        return self.World.data(blink_at, character_at=self._get_coords_of_creature(self.character))

    def get_region_data(self, coords: tuple[int, int], blink_at: tuple[int, int]) -> str:
        return (self.World
                .contents[coords[0]][coords[1]]
                .data(blink_at, character_at=self._get_coords_of_creature(self.character)))

    def get_region_map_details(self, coords: tuple[int, int]) -> list[str]:
        return self.World.contents[coords[0]][coords[1]].map_details

    def get_location_map_details(self, region_coords: tuple[int, int],
                                 location_coords: tuple[int, int]) -> list[str]:
        region = self.World.contents[region_coords[0]][region_coords[1]]
        location = region.contents[location_coords[0]][location_coords[1]]
        return location.map_details

    def _move_character(self, direction: str) -> None:
        direction = self.character.confirm_movement_direction(direction)
        old_coords = self._get_coords_of_creature(self.character)
        new_coords = calculate_new_position(old_coords, direction, *self.World.size)
        old_location = self._current_location
        new_location = self.World.get_location(new_coords)
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
