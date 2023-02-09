import console

tile_size = 5  # Width&height of Tile as container
location_height: int = 21
location_width: int = 78
region_size: int = 1  # Locations per row & column
world_size: int = 9  # Regions per row & column

max_text_lines_on_page: int = 21
max_text_line_length: int = 65

frame_viewing_time: float = 0.07

order_color = console.fg.lightblue
nature_color = console.fg.lightgreen
chaos_color = console.fg.red
hp_color = console.bg.red
mana_color = console.bg.blue
energy_color = console.bg.lightgreen
famine_color = console.bg.lightred
load_color = console.bg.white + console.fg.lightblack
brown_fg_color = console.fg.t_7b3f00
brown_bg_color = console.bg.t_7b3f00

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
# Applied effects
hunger_effect_prefix = "hunger_"
hunger_meat_effect = hunger_effect_prefix + 'meat'
hunger_water_effect = hunger_effect_prefix + 'water'
hunger_rock_effect = hunger_effect_prefix + 'rock'
thirst_effect_prefix = 'thirst_'
thirst_water_effect = thirst_effect_prefix + 'water'
thirst_rock_effect = thirst_effect_prefix + 'rock'
normal_damage_effect = 'normal_damage_effect'
dodge_chance = 'dodge_chance'
# Active character effects
sick_effect = 'Sick'
drunk_effect = 'Drunk'
non_rest_energy_regen_effect = 'non_rest_energy_regen'
non_rest_hp_regen_effect = 'non_rest_hp_regen_effect'
armor_modifier = 'armor_modifier'
travel_energy_loss_modifier = 'travel_energy_loss_modifier'
max_mana_modifier = 'max_mana_modifier'
max_hp_modifier = 'max_hp_modifier'
max_load_modifier = 'max_load_modifier'
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
combat_prefix = "combat"
crafting_prefix = "crafting"
extraction_prefix = "extracting"
social_prefix = "social"
utility_prefix = "utility"
skill_colors = {combat_prefix: console.fg.lightred,
                crafting_prefix: console.fg.lightblue,
                extraction_prefix: console.fg.lightgreen,
                social_prefix: console.fg.yellow,
                utility_prefix: console.fg.purple}
gun_skill = combat_prefix + skill_delimiter + "Guns"
daggers_skill = combat_prefix + skill_delimiter + "Daggers"
onehanded_swords_skill = combat_prefix + skill_delimiter + "1h swords"
twohanded_axes_skill = combat_prefix + skill_delimiter + "2h axes"
unarmed_combat_skill = combat_prefix + skill_delimiter + "Unarmed combat"
improvised_combat_skill = combat_prefix + skill_delimiter + "Improvised weapons"
throwing_knife_skill = combat_prefix + skill_delimiter + "Throwing knives"
mining_skill = extraction_prefix + skill_delimiter + 'Mining'
scavenging_skill = extraction_prefix + skill_delimiter + 'Scavenging'
# Ranged weapon/ammo types
acorn_gun_type = 'acorn_gun_type'

random_creatures_respawn_period = 500
creature_rarity_scale = [1, 1/2, 1/9]

max_stat_value = 20
max_skill_value = 100

if __name__ == '__main__':
    print(len(str(race_selection_title)))
