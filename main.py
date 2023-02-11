from userinterface import UserInterface
from sequence import GameSequence
from game import Game

game = Game()
sequence = GameSequence()
main_screen = UserInterface(game, sequence)
playing = main_screen.process_player_input()
while playing:
    playing = main_screen.process_player_input()
