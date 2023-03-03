from windows import Window, InputWindow, SelectionWindow
import content_types as ct
from game import Game
import config


class GameSequence:
    @staticmethod
    def get_window(ui) -> Window:
        if ui.game.state == Game.welcome_state:
            return Window(ui=ui, content=ct.WindowContent(ui.game))
        elif ui.game.state == Game.ended_state:
            return Window(ui=ui, content=ct.EndedGameContent(ui.game))
        elif ui.game.state == Game.new_game_state and ui.game.substate == Game.character_name_substate:
            return InputWindow(size=(3, 40), top_left=(11, 20), ui=ui, border=True, title='Enter your name',
                               content=ct.TextInputField(35), target=ui.game.set_character_name)
        elif ui.game.state == Game.loading_state and ui.game.substate == Game.saved_game_selection_substate:
            return SelectionWindow(ui=ui, border=True, title=config.saved_game_selection_title,
                                   content=ct.SavedGamesList(ui.game), target=ui.game.load_game)
        elif ui.game.state == Game.new_game_state and ui.game.substate == Game.race_selection_substate:
            return SelectionWindow(ui=ui, border=True, title=config.race_selection_title,
                                   content=ct.SentientSpeciesList(ui.game), target=ui.game.start_game)
        elif ui.game.state == Game.playing_state and ui.game.substate in Game.scene_substates:
            return Window(ui=ui, title_source=ui.game.get_current_location_name, border=True,
                          content=ct.GameScene(ui.game))
        elif ui.game.state == Game.playing_state and ui.game.substate == Game.map_substate:
            return Window(ui=ui, content=ct.MapScreen(ui.game), border=True, title='Map')
        elif ui.game.state == Game.playing_state and ui.game.substate == Game.equip_for_substate:
            return SelectionWindow(ui=ui, content=ct.EquipmentList(ui.game), border=True,
                                   title='What do you want to equip?', target=ui.game.equip_item_from_selection_screen)
        elif ui.game.state == Game.playing_state and ui.game.substate == Game.fill_container_substate:
            return SelectionWindow(ui=ui, content=ct.SubstancesList(ui.game), border=True,
                                   title='Where to fill this container from?', target=ui.game.fill_container)
        elif ui.game.state == Game.playing_state and ui.game.substate == Game.inventory_substate:
            return Window(ui=ui, content=ct.InventoryScreen(ui.game), border=True, title=f'Inventory')
        elif ui.game.state == Game.playing_state and ui.game.substate == Game.character_sheet_substate:
            return Window(ui=ui, content=ct.CharacterSheet(ui.game), border=True, title=f'Character sheet')
        else:
            raise ValueError(f'Unhandled state: {ui.game.state} / {ui.game.substate}')
