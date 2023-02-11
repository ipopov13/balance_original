import console
from console.utils import cls
from console.screen import Screen
import msvcrt

screen_content = '''
               ___      _   _         _   _    _   ___   ____
              |   \    / |  |        / |  |\   |  /   \ |
              |___/   /  |  |       /  |  | \  |  |     |___
              |   \  /---|  |      /---|  |  \ |  |     |
              |___/ /    |  |___| /    |  |   \|  \___/ |____

                                    ver 0.6

                                   (n)ew game
                             (l)oad a previous game
                            '''

cls()
with console.screen.sc.location(0, 0):
    print(screen_content)
sc = Screen()
inputs = 0
while str(inputs) != '1':
    inputs = msvcrt.getch().decode()
    # with console.screen.sc.location(0, 0):
    print(f'{console.style.fx.frame}{ord(inputs)}{console.fx.end}', end='', flush=True)
    print(sc.move_to(8, 5), end='', flush=True)

