import game_objects as go
import console

contained_fire_color_range = [console.fg.lightyellow, console.fg.yellow,
                              console.fg.lightred, console.fg.red]


class Campfire(go.Effect):
    def __init__(self, length: int):
        super().__init__(color_range=contained_fire_color_range, name='a campfire', icon='*',
                         length=length, description='A small fire. It will die soon.')
