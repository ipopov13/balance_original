import console
from console.utils import cls, set_title


class Console:
    """Adapter class for Console"""
    colors = {0: console.fg.black,
        1: console.fg.blue,
        2: console.fg.green,
        3: console.fg.lightblue,
        4: console.fg.red,
        5: console.fg.purple,
        6: console.fg.t_a8a800,
        7: console.fg.lightblack,
        8: console.fg.t_545454,
        9: console.fg.t_5454fc,
        10: console.fg.t_54fc54,
        11: console.fg.t_54fcfc,
        12: console.fg.t_fc5454,
        13: console.fg.t_fc54fc,
        14: console.fg.yellow,
        15: console.fg.white}
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

    @staticmethod
    def scroll(coords, i0, i1, color, char):
        with Console.location(coords[1], coords[0]):
            print(f'{Console.colors[color]}{char}{console.fx.end}')

    @staticmethod
    def text(x, y, text, color):
        with Console.location(y, x):
            print(f'{Console.colors[color]}{text}{console.fx.end}')

# cls()
# with console.screen.sc.location(0, 0):
#     print(screen_content)
# inputs = 0
# while str(inputs) != '1':
#     inputs = msvcrt.getch().decode()
#     with console.screen.sc.location(0, 0):
#         print(f'{console.fg.red+console.bg.green}{str(inputs)}{console.fx.end}')
