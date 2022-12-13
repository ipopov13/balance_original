from display import Display

main_screen = Display()
playing = main_screen.process_player_input()
while playing:
    playing = main_screen.process_player_input()
