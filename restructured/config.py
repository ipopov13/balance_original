import console

max_text_lines_on_page = 21
max_text_line_length = 65

order_color = console.fg.lightblue
nature_color = console.fg.lightgreen
chaos_color = console.fg.red

race_selection_title = (f' In a world of {order_color}Order{console.fx.end}, '
                        f'{nature_color}Nature{console.fx.end}, '
                        f'and {chaos_color}Chaos{console.fx.end}, who are you? ')

if __name__ == '__main__':
    print(len(str(race_selection_title)))
