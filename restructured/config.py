import console

location_height = 21
location_width = 78
region_size = 9
world_size = 9

max_text_lines_on_page = 21
max_text_line_length = 65

order_color = console.fg.lightblue
nature_color = console.fg.lightgreen
chaos_color = console.fg.red
hp_color = console.bg.red
mana_color = console.bg.blue
energy_color = console.bg.lightgreen
load_color = console.bg.white

race_selection_title = (f' In a world of {order_color}Order{console.fx.end}, '
                        f'{nature_color}Nature{console.fx.end}, '
                        f'and {chaos_color}Chaos{console.fx.end}, who are you? ')

if __name__ == '__main__':
    print(len(str(race_selection_title)))
