from typing import Optional
import console
import random
from game_objects import Terrain, FlavorTerrain, LiquidSource, Item, \
    Creature, Container, HumanoidSpecies, Animal, GameObject, Tile
import items
import config
import species as sp
from utils import direct_path, coord_distance

# Ground fillers
grass = Terrain(color=console.fg.lightgreen, name='grass',
                description='Grass.', spawned_creatures=[sp.field_mouse_species])
ashes = Terrain(color=console.fg.lightblack, name='ashes',
                description='Ashes.', spawned_creatures=[sp.ash_beetle_species, sp.rat_species])
dirt = Terrain(color=config.brown_fg_color, name='dirt',
               description='Dirt.', spawned_creatures=[sp.field_mouse_species])
snow = Terrain(color=console.fg.white, name='snow',
               description='Snow.', spawned_creatures=[sp.snow_hare_species],
               effects={config.snow_passage_cost: 2})
sand = Terrain(color=console.fg.yellow, name='sand',
               description='Sand.', spawned_creatures=[sp.sand_snake_species, sp.scorpion_species],
               effects={config.sand_passage_cost: 2})
ice = Terrain(color=console.fg.lightblue, name='ice',
              description='Slippery-looking ice.', spawned_creatures=[sp.ice_mantis_species],
              effects={config.ice_passage_cost: 2})
# Other base terrains
tree = Terrain(color=console.fg.lightgreen, name='tree', icon='T',
               description='A tree.', spawned_creatures=[sp.fox_species, sp.wolf_species])
dead_tree = Terrain(color=console.fg.lightblack, name='dead tree', icon='T',
                    description='A dead-looking tree.',
                    spawned_creatures=[sp.wolf_species, sp.swamp_dragon_species])
frozen_tree = Terrain(color=console.fg.lightblue, name='frozen tree', icon='T',
                      description='An ice-covered tree.',
                      spawned_creatures=[sp.ice_fox_species, sp.winter_wolf_species])
ice_block = Terrain(color=console.fg.lightblue, name='ice block', icon='%', passable=False,
                    description='A huge block of ice.',
                    spawned_creatures=[sp.winter_wolf_species, sp.ice_bear_species],
                    effects={config.ice_climbing_cost: 100})
rocks = Terrain(color=console.fg.lightblack, name='rocks', icon='%', passable=False,
                description='A rock outcropping.',
                spawned_creatures=[sp.bear_species, sp.eagle_species],
                allowed_species=[sp.gnome_race, sp.eagle_species],
                effects={config.rock_climbing_cost: 100})
bush = Terrain(color=console.fg.lightgreen, name='bush', icon='#',
               description='A bush.', spawned_creatures=[sp.fox_species],
               effects={config.plant_passage_cost: 3})
swamp = Terrain(color=console.fg.lightgreen, name='swamp', icon='~',
                description='Swampy ground.',
                spawned_creatures=[sp.crocodile_species, sp.swamp_dragon_species, sp.hydra_species],
                effects={config.wading_passage_cost: 5})
salt_lake = Terrain(color=console.fg.lightyellow, name='salt lake',
                    description='Salt-encrusted water.', spawned_creatures=[sp.crocodile_species],
                    effects={config.wading_passage_cost: 5})
jungle = Terrain(color=console.fg.green, name='tree', icon='T', passable=False,
                 description='Impenetrable jungle.',
                 spawned_creatures=[sp.monkey_species, sp.crocodile_species, sp.jaguar_species],
                 effects={config.plant_passage_cost: 50})
all_base_terrains = [grass, ashes, dirt, snow, sand, ice, tree, dead_tree, frozen_tree, ice_block,
                     rocks, bush, swamp, salt_lake, jungle]
# Flavor terrains
poisonous_flowers = FlavorTerrain(color=console.fg.purple, name='poisonous flowers', icon='*',
                                  required_base_terrains=all_base_terrains, required_climates=config.ALL_CLIMATES)
bones = FlavorTerrain(color=console.fg.lightwhite, name='bones', icon='~',
                      description='Grizzly-looking bones.',
                      required_base_terrains=all_base_terrains, required_climates=config.ALL_CLIMATES,
                      effects={config.bones_passage_cost: 2})
venomous_thorns = FlavorTerrain(color=console.fg.lightgreen, name='venomous thorns', icon='#',
                                description='A bush.',
                                required_base_terrains=all_base_terrains, required_climates=config.ALL_CLIMATES,
                                effects={config.plant_passage_cost: 6})
junk_pile = FlavorTerrain(color=console.fg.lightblack, name='junk pile', icon='o',
                          description='Foul-smelling junk.',
                          required_base_terrains=all_base_terrains, required_climates=config.ALL_CLIMATES,
                          effects={config.junk_pile_passage_cost: 2})
lava = FlavorTerrain(color=console.fg.red, name='lava', icon='~', passable=False,
                     description='A hole with bubbling lava!',
                     required_base_terrains=all_base_terrains, required_climates=[config.HOT_CLIMATE])
gold_vein = FlavorTerrain(color=console.fg.lightyellow, name='gold vein', icon='%', passable=False,
                          description='A rock outcropping.',
                          required_base_terrains=[rocks], required_climates=config.ALL_CLIMATES,
                          allowed_species=[sp.gnome_race, sp.eagle_species],
                          effects={config.rock_climbing_cost: 100})
silver_vein = FlavorTerrain(color=console.fg.lightcyan, name='silver vein', icon='%', passable=False,
                            description='A rock outcropping.',
                            required_base_terrains=[rocks], required_climates=config.ALL_CLIMATES,
                            allowed_species=[sp.gnome_race, sp.eagle_species],
                            effects={config.rock_climbing_cost: 100})
iron_vein = FlavorTerrain(color=console.fg.lightblue, name='iron vein', icon='%', passable=False,
                          description='A rock outcropping.',
                          required_base_terrains=[rocks], required_climates=config.ALL_CLIMATES,
                          allowed_species=[sp.gnome_race, sp.eagle_species],
                          effects={config.rock_climbing_cost: 100})
mossy_rock = FlavorTerrain(color=console.fg.lightgreen, name='mossy rock', icon='%', passable=False,
                           description='A moss-covered boulder.',
                           required_base_terrains=all_base_terrains, required_climates=config.ALL_CLIMATES,
                           allowed_species=[sp.gnome_race, sp.eagle_species],
                           effects={config.rock_climbing_cost: 100})
lichen_clump = FlavorTerrain(color=console.fg.lightgreen, name='lichen clump', icon='o',
                             description='A big clump of lichen.',
                             required_base_terrains=all_base_terrains, required_climates=[config.COLD_CLIMATE])
flowers = FlavorTerrain(color=console.fg.purple, name='flowers', icon='*',
                        description='A patch of flowers.',
                        required_base_terrains=all_base_terrains, required_climates=config.ALL_CLIMATES)
old_pavement = FlavorTerrain(color=console.fg.lightyellow, name='old pavement',
                             description='Old pavement.',
                             required_base_terrains=all_base_terrains, required_climates=config.ALL_CLIMATES)
ruined_wall = FlavorTerrain(color=config.brown_fg_color, name='ruined wall', icon='#', passable=False,
                            description='Ancient wall.',
                            required_base_terrains=all_base_terrains, required_climates=config.ALL_CLIMATES,
                            effects={config.rock_climbing_cost: 100})
engraved_column = FlavorTerrain(color=config.brown_fg_color, name='engraved column', icon='|', passable=False,
                                description='An engraved column.',
                                required_base_terrains=all_base_terrains, required_climates=config.ALL_CLIMATES,
                                effects={config.rock_climbing_cost: 100})
fireplace = FlavorTerrain(color=console.fg.lightyellow, name='fireplace', icon='o',
                          description='A fireplace.',
                          required_base_terrains=all_base_terrains, required_climates=config.ALL_CLIMATES)
farmland = FlavorTerrain(color=console.fg.green + config.brown_bg_color, name='farmland', icon='=',
                         description='A tilled field.',
                         required_base_terrains=[grass, dirt, tree, jungle, bush, swamp],
                         required_climates=config.ALL_CLIMATES)
# Structure building blocks
poisoned_water = Terrain(color=console.fg.lightblack, name='poisoned water', icon='~', description='Murky water.',
                         effects={config.wading_passage_cost: 2})
water = Terrain(color=console.fg.blue, name='water', icon='~', description='Water.',
                effects={config.wading_passage_cost: 2})
# TODO: stilled water field - like a mountain!
stilled_water = Terrain(color=console.fg.white, name='stilled water', icon='%', passable=False,
                        description='A block of stilled water.',
                        effects={config.ice_climbing_cost: 100})
well_terrain = Terrain(color=console.fg.blue, icon='o', name='well', description='A water well.',
                       substances=[
                           LiquidSource(resource=items.water_liquid, name='water well', description='A water well.')])

terrain_transformations = {
    rocks: {config.mining_skill: {'new_terrain': dirt, 'number_of_drops': 10,
                                  'drop_types': [items.Rock], 'drop_weights': [100],
                                  'message': 'You turn the boulder into rubble!'}},
    iron_vein: {config.mining_skill: {'new_terrain': dirt, 'number_of_drops': 10,
                                      'drop_types': [items.Rock, items.IronOre],
                                      'drop_weights': [75, 25],
                                      'message': 'You turn the boulder into rubble!'}},
    gold_vein: {config.mining_skill: {'new_terrain': dirt, 'number_of_drops': 10,
                                      'drop_types': [items.Rock, items.GoldOre],
                                      'drop_weights': [75, 25],
                                      'message': 'You turn the boulder into rubble!'}},
    silver_vein: {config.mining_skill: {'new_terrain': dirt, 'number_of_drops': 10,
                                        'drop_types': [items.Rock, items.SilverOre],
                                        'drop_weights': [75, 25],
                                        'message': 'You turn the boulder into rubble!'}},
    ice_block: {config.mining_skill: {'new_terrain': ice, 'number_of_drops': 10,
                                      'drop_types': [items.IceShard], 'drop_weights': [100],
                                      'message': 'The ice breaks into razor-sharp pieces!'}},
    stilled_water: {config.mining_skill: {'new_terrain': water, 'number_of_drops': 10,
                                          'drop_types': [items.StilledWaterShard], 'drop_weights': [100],
                                          'message': 'The translucent block breaks apart!'}},
    bones: {config.scavenging_skill: {'new_terrain': bones, 'number_of_drops': 3,
                                      'drop_types': [None, items.JunkItem], 'drop_weights': [80, 20],
                                      'message': 'You sift through the pile of bones.'}},
    junk_pile: {config.scavenging_skill: {'new_terrain': junk_pile, 'number_of_drops': 3,
                                          'drop_types': [None, items.JunkItem], 'drop_weights': [40, 60],
                                          'message': 'You sift through the pile of bones.'}},
    tree: {config.scavenging_skill: {'new_terrain': tree, 'number_of_drops': 1,
                                     'drop_types': [None, items.Firewood], 'drop_weights': [40, 60],
                                     'message': 'You try to break a branch off.'}},
    dead_tree: {config.scavenging_skill: {'new_terrain': dead_tree, 'number_of_drops': 4,
                                          'drop_types': [None, items.Firewood], 'drop_weights': [40, 60],
                                          'message': 'You try to break a branch off.'}},
    bush: {config.scavenging_skill: {'new_terrain': bush, 'number_of_drops': 1,
                                     'drop_types': [None, items.Firewood], 'drop_weights': [40, 60],
                                     'message': 'You search for firewood.'}}
}
for terrain_type in terrain_transformations:
    terrain_type.transformations = terrain_transformations[terrain_type]


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
            required_climates=config.ALL_CLIMATES)

base_force_terrains = {
    config.COLD_CLIMATE: {config.NATURE_FORCE: [snow, rocks, tree],
                          config.CHAOS_FORCE: [ice, rocks, ice_block],
                          config.ORDER_FORCE: [snow, frozen_tree, rocks]},
    config.TEMPERATE_CLIMATE: {config.NATURE_FORCE: [grass, tree, bush, rocks],
                               config.CHAOS_FORCE: [ashes, dead_tree, swamp, rocks],
                               config.ORDER_FORCE: [dirt, tree, bush, rocks]},
    config.HOT_CLIMATE: {config.NATURE_FORCE: [sand, rocks, jungle],
                         config.CHAOS_FORCE: [sand, rocks, salt_lake],
                         config.ORDER_FORCE: [sand, rocks, bush]}}
filler_terrains = {
    config.COLD_CLIMATE: {config.NATURE_FORCE: snow,
                          config.CHAOS_FORCE: ice,
                          config.ORDER_FORCE: snow},
    config.TEMPERATE_CLIMATE: {config.NATURE_FORCE: grass,
                               config.CHAOS_FORCE: ashes,
                               config.ORDER_FORCE: dirt},
    config.HOT_CLIMATE: {config.NATURE_FORCE: sand,
                         config.CHAOS_FORCE: sand,
                         config.ORDER_FORCE: sand}}
flavor_terrains = {
    config.COLD_CLIMATE: {config.NATURE_FORCE: [flowers, mossy_rock, lichen_clump, gold_vein, iron_vein, silver_vein],
                          config.CHAOS_FORCE: [bones, junk_pile, poisonous_flowers, venomous_thorns],
                          config.ORDER_FORCE: [ruined_wall, old_pavement, engraved_column, farmland, fireplace]},
    config.TEMPERATE_CLIMATE: {config.NATURE_FORCE: [flowers, mossy_rock, gold_vein, iron_vein, silver_vein],
                               config.CHAOS_FORCE: [bones, junk_pile, poisonous_flowers, venomous_thorns],
                               config.ORDER_FORCE: [ruined_wall, old_pavement, engraved_column, farmland, fireplace]},
    config.HOT_CLIMATE: {config.NATURE_FORCE: [flowers, mossy_rock, gold_vein, iron_vein, silver_vein],
                         config.CHAOS_FORCE: [bones, junk_pile, poisonous_flowers, venomous_thorns, lava],
                         config.ORDER_FORCE: [ruined_wall, old_pavement, engraved_column, farmland, fireplace]}}
structures = {
    config.COLD_CLIMATE: {config.NATURE_FORCE: [],
                          config.CHAOS_FORCE: [],
                          config.ORDER_FORCE: [well]},
    config.TEMPERATE_CLIMATE: {config.NATURE_FORCE: [],
                               config.CHAOS_FORCE: [],
                               config.ORDER_FORCE: [well]},
    config.HOT_CLIMATE: {config.NATURE_FORCE: [],
                         config.CHAOS_FORCE: [],
                         config.ORDER_FORCE: [well]}}


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
    region_names = {config.COLD_CLIMATE: {snow: 'Frost lands',
                                          frozen_tree: 'Frozen glade',
                                          tree: 'Winter woods',
                                          ice: 'Ice fields',
                                          ice_block: 'Glacier',
                                          rocks: 'Snowy peaks'},
                    config.TEMPERATE_CLIMATE: {grass: 'Plains',
                                               tree: 'Forest',
                                               bush: 'Bushland',
                                               ashes: 'Wasteland',
                                               swamp: 'Marshlands',
                                               dead_tree: 'Deadwood',
                                               dirt: 'Fields',
                                               rocks: 'Mountains'},
                    config.HOT_CLIMATE: {sand: 'Desert',
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
        name = f'{config.force_colors[self._main_force]}{raw_name}{console.fx.end}'
        super().__init__(height=config.region_size, width=config.region_size,
                         name=name, icon=self._main_terrain.raw_icon, color=self._main_terrain.color)

    @property
    def map_details(self) -> list[str]:
        colored_force = config.force_colors[self._main_force] + self._main_force + console.fx.end
        colored_climate = config.climate_colors[self._climate] + self._climate + console.fx.end
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
        forces = {config.NATURE_FORCE: 33, config.CHAOS_FORCE: 33, config.ORDER_FORCE: 33}
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
    region_suffixes = {config.CHAOS_FORCE: """of Blood
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
                       config.ORDER_FORCE: """of Bread
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
                       config.NATURE_FORCE: """of the Bear
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
        forces = [config.NATURE_FORCE, config.ORDER_FORCE, config.CHAOS_FORCE] * (config.world_size ** 2 // 3 + 1)
        random.shuffle(forces)
        self._contents: Optional[list[list[Region]]] = []
        suffixes = World.region_suffixes.copy()
        for f in suffixes:
            random.shuffle(suffixes[f])
        for row in range(self._height):
            region_list = []
            for column in range(self._width):
                main_force = forces.pop()
                climate = random.choice([config.COLD_CLIMATE, config.TEMPERATE_CLIMATE, config.HOT_CLIMATE])
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
