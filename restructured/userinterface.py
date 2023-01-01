import console
from console.utils import cls
import msvcrt


class UserInterface:
    def __init__(self, game, game_sequence):
        self.game = game
        self.sc = console.screen.Screen(swap=False)
        self._game_sequence = game_sequence
        self._screens = []
        cls()
        self._refresh()

    def _refresh(self):
        if not self._screens:
            cls()
            self._screens.append(self._game_sequence.get_window(self))
        display_data = self._top_screen.get_display_data()
        self.display(display_data)

    @property
    def _top_screen(self):
        return self._screens[-1]

    def process_player_input(self) -> bool:
        """
        Read a character from the input and send it to the window.
        Called by the main loop
        """
        # TODO: This cannot decode arrow keys, add an exception for this
        #  (but it's good for breaking out of endless loops during development)
        player_input = msvcrt.getch().decode()
        result = self._top_screen.handle_input(player_input)
        if not result:
            cls()
        return result

    def drop_window(self, window) -> bool:
        self._screens.remove(window)
        self._refresh()
        return True

    def add_window(self, window) -> bool:
        self._screens.append(window)
        self._refresh()
        return True

    def is_top(self, window) -> bool:
        return window is self._top_screen

    def display(self, updates: tuple[dict, tuple[int, int]]):
        """
        Display the data sent by the window
        updates: {'drop': Window,
                  'update': {coords: update_string},
                  'add': Window}
        """
        content_dict, cursor_pos = updates
        for coordinates, update_string in content_dict.items():
            with self.sc.hidden_cursor():
                with console.screen.sc.location(*coordinates):
                    print(update_string, end='', flush=True)
        print(self.sc.move_to(*cursor_pos), end='', flush=True)
        return True
