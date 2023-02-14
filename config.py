import console

tile_size = 5  # Width&height of Tile as container
location_height: int = 21
location_width: int = 78
region_size: int = 1  # Locations per row & column
world_size: int = 9  # Regions per row & column

max_text_lines_on_page: int = 21
max_text_line_length: int = 65

frame_viewing_time: float = 0.07

hp_color = console.bg.red
mana_color = console.bg.blue
energy_color = console.bg.lightgreen
famine_color = console.bg.lightred
load_color = console.bg.white + console.fg.lightblack
brown_fg_color = console.fg.t_7b3f00
brown_bg_color = console.bg.t_7b3f00

# Forces and climate
order_color = console.fg.lightblue
nature_color = console.fg.lightgreen
chaos_color = console.fg.red
NATURE_FORCE = 'Nature'
CHAOS_FORCE = 'Chaos'
ORDER_FORCE = 'Order'
force_colors = {NATURE_FORCE: nature_color,
                CHAOS_FORCE: chaos_color,
                ORDER_FORCE: order_color}
COLD_CLIMATE = 'Cold'
TEMPERATE_CLIMATE = 'Temperate'
HOT_CLIMATE = 'Hot'
ALL_CLIMATES = [COLD_CLIMATE, HOT_CLIMATE, TEMPERATE_CLIMATE]
climate_colors = {COLD_CLIMATE: console.fg.lightblue,
                  TEMPERATE_CLIMATE: console.fg.lightgreen,
                  HOT_CLIMATE: console.fg.lightred}

multiple_items_icon = '?'
target_cross_icon = console.fg.lightred + 'X' + console.fx.end
target_path_icon = console.fg.yellow + '*' + console.fx.end
race_selection_title = (f' In a world of {order_color}Order{console.fx.end}, '
                        f'{nature_color}Nature{console.fx.end}, '
                        f'and {chaos_color}Chaos{console.fx.end}, who are you? ')
ground = 'Ground'
equipment_title = 'Equipment'
empty_string = '(empty)'
# AI
indifferent_disposition = 'indifferent'
aggressive_disposition = 'aggressive'
fearful_disposition = 'fearful'
chase_humanoid_behavior = 'chase_humanoid'
random_behavior = 'random'
run_from_humanoid_behavior = 'run_from_humanoid'
# Races
Human = "Human"
Dwarf = "Dwarf"
Elf = "Elf"
Gnome = "Gnome"
Orc = "Orc"
Troll = "Troll"
Kraken = "Kraken"
Goblin = "Goblin"
Imp = "Imp"
Fae = "Fae"
Dryad = "Dryad"
Shifter = "Shifter"
WaterElemental = "Water elemental"
# Stats
Str = "Strength"
End = "Endurance"
Dex = "Dexterity"
Per = "Perception"
Wil = "Willpower"
stats_order = [Str, End, Dex, Per, Wil]
# Item effects
#  Consumables
consumable_effects = 'consumable_effects'
hunger_effect_prefix = "hunger_"
hunger_meat_effect = hunger_effect_prefix + 'meat'
hunger_water_effect = hunger_effect_prefix + 'water'
hunger_rock_effect = hunger_effect_prefix + 'rock'
thirst_effect_prefix = 'thirst_'
thirst_water_effect = thirst_effect_prefix + 'water'
thirst_rock_effect = thirst_effect_prefix + 'rock'
#  Combat
combat_effects = 'combat_effects'
ranged_combat = 'ranged_combat'
melee_combat = 'melee_combat'
damage_effect_prefix = 'damage_'
physical_damage = damage_effect_prefix + 'Physical damage'
fire_damage = damage_effect_prefix + 'Fire damage'
#  Resistances, affinities, and modifiers
resistances_and_affinities = 'resistances_and_affinities'
effect_modifiers = 'effect_modifiers'
travel_energy_loss_modifier = 'Travel fatigue'
max_mana_modifier = 'Max mana'
max_hp_modifier = 'Max HP'
max_load_modifier = 'Max load'
max_energy_modifier = 'Max energy'
# Melee combat
max_dodge_chance = 0.8  # 1 = 100%
dodge_difficulty = 'dodge_difficulty'
# Active character effects
sick_effect = 'Sick'
drunk_effect = 'Drunk'
non_rest_energy_regen_effect = 'non_rest_energy_regen'
non_rest_hp_regen_effect = 'non_rest_hp_regen_effect'
# Visible effect values are shown as statuses
visible_effects = [sick_effect, drunk_effect]
# Equipment slots
main_hand_slot = 'Main hand'
offhand_slot = 'Offhand'
head_slot = 'Head'
armor_slot = 'Armor'
back_slot = 'Back'
boots_slot = 'Boots'
animal_weapon_slot = 'AnimalWeapon'
animal_armor_slot = 'AnimalArmor'
animal_meat_slot = 'Meat'
# Skills and prefixes for coloring
skill_delimiter = "_"
combat_skill_prefix = "combat"
crafting_skill_prefix = "crafting"
extraction_skill_prefix = "extracting"
social_skill_prefix = "social"
utility_skill_prefix = "utility"
skill_colors = {combat_skill_prefix: console.fg.lightred,
                crafting_skill_prefix: console.fg.lightblue,
                extraction_skill_prefix: console.fg.lightgreen,
                social_skill_prefix: console.fg.yellow,
                utility_skill_prefix: console.fg.purple}
animal_innate_weapon_skill = combat_skill_prefix + skill_delimiter + "Innate weapons"
gun_skill = combat_skill_prefix + skill_delimiter + "Guns"
bow_skill = combat_skill_prefix + skill_delimiter + "Bows"
crossbow_skill = combat_skill_prefix + skill_delimiter + "Crossbows"
sling_skill = combat_skill_prefix + skill_delimiter + "Slings"
daggers_skill = combat_skill_prefix + skill_delimiter + "Daggers"
onehanded_swords_skill = combat_skill_prefix + skill_delimiter + "Swords"
onehanded_axes_skill = combat_skill_prefix + skill_delimiter + "Axes"
onehanded_hammers_skill = combat_skill_prefix + skill_delimiter + "Maces"
twohanded_swords_skill = combat_skill_prefix + skill_delimiter + "Great swords"
twohanded_axes_skill = combat_skill_prefix + skill_delimiter + "Great axes"
twohanded_hammers_skill = combat_skill_prefix + skill_delimiter + "Great hammers"
staves_skill = combat_skill_prefix + skill_delimiter + "Staves"
spear_skill = combat_skill_prefix + skill_delimiter + "Spears"
throwing_knife_skill = combat_skill_prefix + skill_delimiter + "Throwing knives"
grenades_skill = combat_skill_prefix + skill_delimiter + "Grenades"
throwing_spear_skill = combat_skill_prefix + skill_delimiter + "Throwing spears"
improvised_combat_skill = combat_skill_prefix + skill_delimiter + "Improvised weapons"
unarmed_combat_skill = combat_skill_prefix + skill_delimiter + "Unarmed combat"
shield_skill = combat_skill_prefix + skill_delimiter + "Shields"
evasion_skill = combat_skill_prefix + skill_delimiter + "Evasion"
light_armor_skill = combat_skill_prefix + skill_delimiter + "Light armor"
heavy_armor_skill = combat_skill_prefix + skill_delimiter + "Heavy armor"
mining_skill = extraction_skill_prefix + skill_delimiter + 'Mining'
scavenging_skill = extraction_skill_prefix + skill_delimiter + 'Scavenging'
monster_harvesting_skill = extraction_skill_prefix + skill_delimiter + 'Monster harvesting'
# Ranged weapon/ammo types
hand_thrown_type = 'hand_thrown_type'
acorn_gun_type = 'acorn_gun_type'
gun_type = 'gun_type'
bow_type = 'bow_type'
crossbow_type = 'crossbow_type'
ballista_type = 'ballista_type'
sling_type = 'sling_type'

random_creatures_respawn_period = 500
creature_rarity_scale = [1, 1/2, 1/9]

max_stat_value = 20
max_skill_value = 100

if __name__ == '__main__':
    print(len(str(race_selection_title)))
