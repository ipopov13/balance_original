import game_objects as go
import items
import console

contained_fire_color_range = [console.fg.lightyellow, console.fg.yellow,
                              console.fg.lightred, console.fg.red]


class Campfire(go.Effect):
    def __init__(self, duration: int, tile: go.Tile):
        super().__init__(color_range=contained_fire_color_range, duration=duration, tile=tile,
                         name='a campfire', description='A small campfire.')
        self._campfire = go.PowerSource(resource=items.fire_power, contained_amount=duration,
                                        name='a {} campfire', description='A campfire.')
        self._tile.add_item(self._campfire)

    def _tick_specific_effects(self, creature: go.Creature = None) -> None:
        if self.duration == 0:
            self._tile.remove_item(self._campfire)
        else:
            self._campfire.contained_amount = self.duration

    def _effects_on_duration_change(self) -> None:
        self._tick_specific_effects()
