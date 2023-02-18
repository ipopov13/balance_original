import game_objects as go
import items
import console

contained_fire_color_range = [console.fg.lightyellow, console.fg.yellow,
                              console.fg.lightred, console.fg.red]


class Campfire(go.PowerSource, go.Effect):
    def __init__(self, length: int):
        super().__init__(resource=items.fire_power, contained_amount=length,
                         color_range=contained_fire_color_range, length=length,
                         name='a campfire', description='A small campfire.')
