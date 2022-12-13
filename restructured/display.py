import console
from console.utils import cls
import msvcrt
from windows import Window, WelcomeWindow


class Display:
    def __init__(self):
        self._screens: [Window] = [WelcomeWindow()]
        cls()
        self._show()

    def _show(self):
        display_data = self._top_screen.get_display_data()
        for row_index, row in enumerate(display_data):
            with console.screen.sc.location(row_index, 0):
                print(row)

    @property
    def _top_screen(self) -> Window:
        return self._screens[-1]

    def process_player_input(self) -> bool:
        player_input = msvcrt.getch().decode()
        response = self._top_screen.interfaces.get(player_input, self._empty_response)
        return response(player_input)

    @staticmethod
    def _empty_response(_):
        return True
