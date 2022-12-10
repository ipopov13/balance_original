import console
from console.utils import cls, set_title


class Console:
    """Adapter class for Console"""

    location = console.screen.sc.location

    @staticmethod
    def getconsole():
        return Console()

    @staticmethod
    def title(title_string):
        set_title(title_string)

    @staticmethod
    def cursor(_):
        pass

    @staticmethod
    def page():
        cls()

    @staticmethod
    def write(text):
        print(text)

    @staticmethod
    def rectangle(coords):
        x_start, y_start, x_end, y_end = coords
        line_length = x_end - x_start - 1
        for y in range(y_start, y_end):
            with Console.location(y, x_start):
                print(' ' * line_length)

# cls()
# with console.screen.sc.location(0, 0):
#     print(screen_content)
# inputs = 0
# while str(inputs) != '1':
#     inputs = msvcrt.getch().decode()
#     with console.screen.sc.location(0, 0):
#         print(f'{console.fg.red+console.bg.green}{str(inputs)}{console.fx.end}')
