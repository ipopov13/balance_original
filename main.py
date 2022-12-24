import console
from console.utils import cls
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
inputs = 0
while str(inputs) != '1':
    inputs = msvcrt.getch().decode()
    with console.screen.sc.location(0, 0):
        print(f'{console.fg.red+console.bg.green}{ord(inputs)}{console.fx.end}')
