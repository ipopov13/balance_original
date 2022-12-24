"""
The Game defines:
  # TODO: Write out the sequence of windows and commands that can happen
  the sequence of windows that the UI should display
  the objects to be passed to the windows as input
  what window content type the objects will be displayed with
  holds all the required game Objects as references
  is attached to the UI

The game Objects:
  provide the object-related commands the window content should pass to the window
  define which game logic should be called after those commands are received
  are manipulated by the logic of the game
  provide the trigger for the logic via the callback methods

The game Logic:
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
      SelectRace runs the ApplyRace & ChooseStartingLocation Logic (character, specific race),
        closes RaceSelection and opens MainScene Window

The UI:
  organizes the display of the game
  handles display calls from the windows
  maintains a stack of windows to choose from
  receives the player input
  passes the input to the top window for execution

The Windows:
  have some game content to use as input
  generate display data to show this content
  support generic window-related commands
  call back the methods they were handed by the content

The window Content:
  supports functions like pagination and item selection

"""