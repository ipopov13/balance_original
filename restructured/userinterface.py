import console
from console.utils import cls
import msvcrt
from windows import Window, WelcomeWindow


class UserInterface:
    def __init__(self):
        self._screens: [Window] = [WelcomeWindow(ui=self)]
        cls()
        display_data = self._top_screen.get_display_data()
        self.display(display_data)

    @property
    def _top_screen(self) -> Window:
        return self._screens[-1]

    def process_player_input(self) -> bool:
        """
        Read a character from the input and send it to the window.
        Called by the main loop
        """
        player_input = msvcrt.getch().decode()
        return self._top_screen.handle_input(player_input)

    @staticmethod
    def display(updates):
        """
        Display the data sent by the window
        updates: {'drop': Window,
                  'update': {coords: update_string},
                  'add': Window}
        """
        if not updates:
            return False
        for coordinates, update_string in updates['update'].items():
            with console.screen.sc.location(*coordinates):
                print(update_string)
        return True
