import console

tile_size = 5  # Width&height of Tile as container
location_height: int = 21
location_width: int = 78
region_size: int = 1  # Locations per row & column
world_size: int = 9  # Regions per row & column

max_text_lines_on_page: int = 21
max_text_line_length: int = 65

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
race_selection_title = (f' In a world of {order_color}Order{console.fx.end}, '
                        f'{nature_color}Nature{console.fx.end}, '
                        f'and {chaos_color}Chaos{console.fx.end}, who are you? ')
ground = 'Ground'
equipment_title = 'Equipment'
empty_string = '(empty)'
indifferent_disposition = 'indifferent'
aggressive_disposition = 'aggressive'
fearful_disposition = 'fearful'
chase_humanoid_behavior = 'chase_humanoid'
random_behavior = 'random'
run_from_humanoid_behavior = 'run_from_humanoid'

hunger_effect_prefix = "hunger_"
hunger_meat_effect = hunger_effect_prefix + 'meat'
hunger_water_effect = hunger_effect_prefix + 'water'
hunger_rock_effect = hunger_effect_prefix + 'rock'
thirst_effect_prefix = 'thirst_'
thirst_water_effect = thirst_effect_prefix + 'water'
thirst_rock_effect = thirst_effect_prefix + 'rock'
# Active character effects
sick_effect = 'Sick'
drunk_effect = 'Drunk'
non_rest_energy_regen_effect = 'non_rest_energy_regen'
non_rest_hp_regen_effect = 'non_rest_hp_regen_effect'
armor_modifier = 'armor_modifier'
travel_energy_loss_modifier = 'travel_energy_loss_modifier'
max_mana_modifier = 'max_mana_modifier'
max_hp_modifier = 'max_hp_modifier'
# Visible effect values are shown as statuses
visible_effects = [sick_effect, drunk_effect]
# Tools
skill_mining = 'skill_mining'
# Equipment slots
main_hand_slot = 'Main hand'

random_creatures_respawn_period = 1  # 500
creature_rarity_scale = [1, 1/2, 1/9]

max_stat_value = 20

if __name__ == '__main__':
    print(len(str(race_selection_title)))
