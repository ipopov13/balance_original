from userinterface import UserInterface
from sequence import GameSequence
from game import Game


def get_new_main_screen() -> UserInterface:
    game = Game()
    sequence = GameSequence()
    return UserInterface(game, sequence)


main_screen = get_new_main_screen()
playing = main_screen.process_player_input()
while playing:
    playing = main_screen.process_player_input()
    if not playing:
        main_screen = get_new_main_screen()
        playing = True
