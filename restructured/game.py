"""
The UI (what does the player see?):
  displays the game
  Asks the Game for a window when there is none
  handles display calls from the windows
  maintains a stack of windows to choose from
  receives the player input
  passes the input to the top window for execution

The Game (what happens next?):
  # TODO: Write out the sequence of windows and commands that can happen
  defines the sequence of windows that the UI should display (welcome, [race, name] | [load game], scene, [highscore])
  answers get_window() calls from the UI based on the current state
  defines the objects to be displayed
  holds all the required game Objects as references
  is injected into the UI at the start

The game Objects (what is displayed?):
  define what window content type they are displayed with
  provide the object-related commands the window content should pass to the window
  define which game logic should be called after those commands are received
  use the Logic to interact with one another
  provide callback methods to be used when a command is triggered

The game Logic (what happens now?):
  is disconnected from the actual objects
  is used by the objects to generate commands
  receives objects as input
  applies changes to the objects once the commands are triggered
  EXAMPLE: ChangeName changes the name of a game object
  EXAMPLE: LivingWorld executes the changes in an area of the world
  can call other logics to create its effects
  EXAMPLE: LivingWorld calls Combat to resolve the result of aggressive bumps

The Commands:
  can do two things: change the UI (add/remove Windows, update Content state) and run Logic
  they can do both things, or only one
  EXAMPLE:
      OpenContainer shows a Window without any game changes
      A Move command changes the "selected" item in the Content (the Object is still unchanged, no Logic is run)
      A Take command runs the MoveItem Logic with the container, the item, and the bag as arguments
      CloseContainer drops the open Window
  EXAMPLE:
      NewGame runs the CreateCharacter & CreateWorld Logic (on the Game) and adds the NameInput window
      The EnterName command runs ChangeName Logic (character & name input), closes NameInput
        and opens RaceSelection Window
      NextPage changes the state of the window Content to show more races
      SelectRace runs the ApplyRace(character, specific race) & ApplyStartingLocation(game, character) Logics,
        closes RaceSelection and opens MainScene Window

The Windows (where are things displayed?):
  have some game content to use as input
  generate display data to show this content
  support generic window-related commands
  call back the methods they were handed by the content

The window Content (how are things displayed?):
  supports functions like pagination and item selection

"""
from game_objects import WelcomeScreen


class Game:
    def __init__(self):
        self.character = None

    def get_window(self):
        if self.character is None:
            current_object = WelcomeScreen(self)
        return current_object.display()
