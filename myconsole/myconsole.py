# import console
from console.utils import cls, set_title


class Console:
    """Adapter class for Console"""
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

# cls()
# with console.screen.sc.location(0, 0):
#     print(screen_content)
# inputs = 0
# while str(inputs) != '1':
#     inputs = msvcrt.getch().decode()
#     with console.screen.sc.location(0, 0):
#         print(f'{console.fg.red+console.bg.green}{str(inputs)}{console.fx.end}')
