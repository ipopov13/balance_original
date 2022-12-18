"""
The Game defines:
  # TODO: Write out the sequence of windows and commands that can happen
  the sequence of windows that the UI should display
  the objects to be passed to the windows as input
  what window content type the objects will be displayed with

The game objects:
  provide the object-related commands the window content should pass to the window
  define which game logic should be called after those commands are received
  are manipulated by the logic of the game
  provide the trigger for the logic via the callback methods

The game logic:
  is disconnected from the actual objects
  is used by the objects to generate commands
  receives objects as input
  applies changes to the objects once the commands are triggered
  EXAMPLE: ChangeName changes the name of a game object
  EXAMPLE: LivingWorld executes the changes in an area of the world
  can call other logics to create its effects
  EXAMPLE: LivingWorld calls Combat to resolve the result of aggressive bumps

The UI:
  organizes the display of the game
  handles display calls from the windows
  maintains a stack of windows to choose from
  receives the player input
  passes the input to the top window for execution

The windows:
  have some game content to use as input
  generate display data to show this content
  support generic window-related commands
  call back the methods they were handed by the content

The window content:
  supports functions like pagination and item selection

"""