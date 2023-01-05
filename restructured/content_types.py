import commands
import config
import console


class WindowContent:
    def __init__(self, game_object):
        self.game_object = game_object

    @staticmethod
    def _own_commands() -> dict:
        return {}

    def commands(self) -> dict:
        """Combine the content-specific and object-specific commands"""
        return {**self._object_commands(),
                **self._own_commands()}

    def data(self) -> str:
        return self.game_object.data()

    def cursor_pos(self) -> tuple[int, int]:
        return 0, 0

    def _object_commands(self) -> dict:
        """The mapping of commands&methods specific for the underlying object(s)"""
        try:
            object_commands = self.game_object.commands()
        except AttributeError:
            object_commands = {}
            for obj in self.game_object:
                object_commands.update(obj.commands())
        return object_commands


class GameScene(WindowContent):
    def data(self) -> str:
        character_hud = self.game_object.get_character_hud()
        area_view = self.game_object.get_area_view()
        return '\n'.join([area_view, character_hud])

    def cursor_pos(self) -> tuple[int, int]:
        return self.game_object.get_character_position_in_location()


class EquipmentScreen(WindowContent):
    def data(self) -> str:
        equipment_slot, equipment = self.game_object.get_equipment_data()
        content = []
        for number, (slot, item) in enumerate(equipment.items(), 1):
            item_name = 'empty' if item is None else item.name
            content.append(f'{number}) {slot}: {item_name}')
        return '\n'.join(content)


class MapScreen(WindowContent):
    WORLD = 'World'
    REGION = 'Region'

    def __init__(self, game_object):
        super().__init__(game_object)
        self._active_map = MapScreen.WORLD
        self._map_top_left = {MapScreen.WORLD: (1, 1),
                              MapScreen.REGION: (4 + config.world_size, 1)}
        self._selected_pos = (0, 0)

    def _own_commands(self) -> dict:
        return {commands.SwitchMaps(): self._switch_maps}

    def _switch_maps(self, _) -> bool:
        if self._active_map is MapScreen.WORLD:
            self._active_map = MapScreen.REGION
        else:
            self._active_map = MapScreen.WORLD
        return True

    def _prettify_map(self, map_name: str = None, map_: str = None, map_size: int = None):
        border_color = console.fg.default if map_name is self._active_map else console.fx.dim
        return '\n'.join([border_color + map_name.center(map_size + 2, '-') + console.fx.end,
                          ' ' + map_.replace('\n', '\n '),
                          border_color + '-' * (map_size + 2) + console.fx.end])

    def data(self) -> str:
        world_map = self.game_object.get_world_data()
        pretty_world_map = self._prettify_map(MapScreen.WORLD, world_map, config.world_size)
        region_map = self.game_object.get_region_data()
        pretty_region_map = self._prettify_map(MapScreen.REGION, region_map, config.region_size)
        return '\n\n'.join([pretty_world_map, pretty_region_map])

    def cursor_pos(self) -> tuple[int, int]:
        return self._map_top_left[self._active_map][0] + self._selected_pos[0], \
            self._map_top_left[self._active_map][1] + self._selected_pos[1]


class PagedList(WindowContent):
    def __init__(self, game_object):
        super().__init__(game_object)
        sorted_list = sorted(self.game_object, key=lambda x: x.sort_key)
        self._item_descriptions = [f'{console.fg.yellow}#)'
                                   f' {self._line_up(f"{item.name}: {item.description}")}'
                                   .replace(f'{item.name}:', f'{item.color + item.name}:{console.fx.end}')
                                   for number, item in enumerate(sorted_list)]
        description_lines = [len(desc.split('\n')) for desc in self._item_descriptions]
        self._pages = self._paginate(description_lines)
        self._current_page = 0

    def commands(self) -> dict:
        return {commands.NextPage(): self._next_page,
                commands.PreviousPage(): self._previous_page}

    def _next_page(self, _):
        self._current_page = min(self._current_page + 1, len(self._pages) - 1)

    def _previous_page(self, _):
        self._current_page = max(self._current_page - 1, 0)

    def return_object(self, object_number_in_page_as_string):
        absolute_object_number = self._pages[self._current_page][0] + int(object_number_in_page_as_string)
        return self.game_object[absolute_object_number]

    def _current_page_content(self):
        curr_start, curr_end = self._pages[self._current_page]
        return self._item_descriptions[curr_start:curr_end]

    def data(self) -> str:
        contents = self._current_page_content()
        numbered_contents = [content.replace('#)', f'{n})') for content, n
                             in zip(contents, range(len(contents)))]
        hint_line = ' ' * config.max_text_line_length
        if self._current_page < len(self._pages) - 1:
            hint = commands.NextPage.hint
            hint_line = hint_line[:-1 * len(hint)] + hint
        if self._current_page > 0:
            hint = commands.PreviousPage.hint
            hint_line = hint + hint_line[len(hint):]
        final_contents = numbered_contents + [hint_line]
        return '\n'.join(final_contents)

    @staticmethod
    def _paginate(contents) -> [(int, int)]:
        # TODO: Write a test for the 10 lines rule!
        pages = []
        current_size = 0
        current_start_index = 0
        for i, content in enumerate(contents):
            if current_size + content > config.max_text_lines_on_page \
                    or i - current_start_index > 10:
                pages.append((current_start_index, i))
                current_size = content
                current_start_index = i
                continue
            current_size += content
        if current_size:
            pages.append((current_start_index, len(contents)))
        return pages

    @property
    def max_choice(self):
        return len(self._current_page_content())

    @staticmethod
    def _line_up(text: str) -> str:
        """Turn the text into a multiline string"""
        lines = []
        text = text.strip()
        line_limit = config.max_text_line_length
        while text:
            if len(text) > line_limit:
                a_line = text[:line_limit].rsplit(' ', 1)[0]
            else:
                a_line = text
            padding = '' if not lines else '   '
            lines.append(padding + a_line.strip())
            text = text[len(a_line):].strip()
        return '\n'.join(lines)


class DescriptionList(WindowContent):
    """Generate a list of object descriptions from an iterable"""

    def data(self) -> str:
        command_descriptions = [f'{k.character}: {k.description}' for k in self.game_object]
        return '\n'.join(command_descriptions)


class TextInputField:
    def __init__(self):
        self._data = ''

    def commands(self) -> dict:
        return {commands.TextInput(): self._add_character,
                commands.Backspace(): self._remove_last_character}

    def _add_character(self, character):
        self._data += character

    def _remove_last_character(self, _):
        self._data = self._data[:-1]

    def data(self) -> str:
        return self._data

    def cursor_pos(self) -> tuple[int, int]:
        return 0, len(self._data)
