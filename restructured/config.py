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
aggressive_disposition = 'indifferent'
fearful_disposition = 'indifferent'
chase_humanoid_behavior = 'chase_humanoid'
random_behavior = 'random'

random_creatures_respawn_period = 1  # 500
creature_rarity_scale = [1, 1/2, 1/9]

max_stat_value = 20

if __name__ == '__main__':
    print(len(str(race_selection_title)))
