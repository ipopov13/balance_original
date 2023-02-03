from windows import Window, InputWindow, SelectionWindow
import content_types as ct
from game_objects import Game
import config


class GameSequence:
    @staticmethod
    def get_window(ui) -> Window:
        if ui.game.state is Game.welcome_state:
            return Window(ui=ui, content=ct.WindowContent(ui.game))
        elif ui.game.state is Game.new_game_state and ui.game.substate is Game.character_name_substate:
            return InputWindow(size=(3, 20), top_left=(11, 30), ui=ui, border=True, title='Enter your name',
                               content=ct.TextInputField(), target=ui.game.set_character_name)
        elif ui.game.state is Game.new_game_state and ui.game.substate is Game.race_selection_substate:
            return SelectionWindow(ui=ui, border=True, title=config.race_selection_title,
                                   content=ct.SentientSpeciesList(ui.game), target=ui.game.start_game)
        elif ui.game.state is Game.playing_state and ui.game.substate in [Game.scene_substate,
                                                                          Game.working_substate,
                                                                          Game.looking_substate]:
            return Window(ui=ui, title_source=ui.game.get_current_location_name, border=True,
                          content=ct.GameScene(ui.game))
        elif ui.game.state is Game.playing_state and ui.game.substate is Game.map_substate:
            return Window(ui=ui, content=ct.MapScreen(ui.game), border=True, title='Map')
        elif ui.game.state is Game.playing_state and ui.game.substate is Game.equip_for_substate:
            return SelectionWindow(ui=ui, content=ct.EquipmentList(ui.game), border=True,
                                   title='What do you want to equip?', target=ui.game.equip_item_from_selection_screen)
        elif ui.game.state is Game.playing_state and ui.game.substate is Game.fill_container_substate:
            return SelectionWindow(ui=ui, content=ct.SubstancesList(ui.game), border=True,
                                   title='Where to fill this container from?', target=ui.game.fill_container)
        elif ui.game.state is Game.playing_state and ui.game.substate is Game.inventory_substate:
            return Window(ui=ui, content=ct.InventoryScreen(ui.game), border=True, title=f'Inventory')
        elif ui.game.state is Game.playing_state and ui.game.substate is Game.character_sheet_substate:
            return Window(ui=ui, content=ct.CharacterSheet(ui.game.character), border=True, title=f'Character sheet')
        else:
            raise ValueError(f'Unhandled state: {ui.game.state} / {ui.game.substate}')
