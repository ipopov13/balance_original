from windows import Window, InputWindow, SelectionWindow
from content_types import WindowContent, TextInputField, GameScene, MapScreen, \
    EquipmentList, SentientSpeciesList, InventoryScreen
from game_objects import Game
import config


class GameSequence:
    @staticmethod
    def get_window(ui) -> Window:
        if ui.game.state is Game.welcome_state:
            return Window(ui=ui, content=WindowContent(ui.game))
        elif ui.game.state is Game.new_game_state and ui.game.substate is Game.character_name_substate:
            return InputWindow(size=(3, 20), top_left=(11, 30), ui=ui, border=True, title='Enter your name',
                               content=TextInputField(), target=ui.game.set_character_name)
        elif ui.game.state is Game.new_game_state and ui.game.substate is Game.race_selection_substate:
            return SelectionWindow(ui=ui, border=True, title=config.race_selection_title,
                                   content=SentientSpeciesList(ui.game), target=ui.game.start_game)
        elif ui.game.state is Game.playing_state and ui.game.substate is Game.scene_substate:
            return Window(ui=ui, title_source=ui.game.get_current_location_name, border=True,
                          content=GameScene(ui.game))
        elif ui.game.state is Game.playing_state and ui.game.substate is Game.map_substate:
            return Window(ui=ui, content=MapScreen(ui.game), border=True, title='Map')
        elif ui.game.state is Game.playing_state and ui.game.substate is Game.equip_for_substate:
            return SelectionWindow(ui=ui, content=EquipmentList(ui.game), border=True,
                                   title='What do you want to equip?', target=ui.game.equip_item)
        elif ui.game.state is Game.playing_state and ui.game.substate is Game.inventory_substate:
            return Window(ui=ui, content=InventoryScreen(ui.game), border=True, title=f'Inventory')
        else:
            raise ValueError(f'Unhandled state: {ui.game.state} / {ui.game.substate}')
