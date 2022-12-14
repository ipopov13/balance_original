from userinterface import UserInterface

main_screen = UserInterface()
playing = main_screen.process_player_input()
while playing:
    playing = main_screen.process_player_input()
