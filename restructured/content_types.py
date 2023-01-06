import commands
import config
import console


class WindowContent:
    def __init__(self, game_object):
        self.game_object = game_object
        self._own_commands = {}

    def commands(self) -> dict:
        """Combine the content-specific and object-specific commands"""
        return {**self._object_commands(),
                **self._own_commands}

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
    def __init__(self, game_object):
        super().__init__(game_object)
        self._own_commands = {}
        equipment = self.game_object.get_equipment_data()
        self._listing = dict(enumerate(equipment.items()))
        self._content = []
        for number, (slot, item) in self._listing.items():
            item_name = 'empty' if item is None else item.name
            self._content.append(f'{number}) {slot}: {item_name}')

    def data(self) -> str:
        return '\n'.join(self._content)

    @property
    def max_choice(self) -> int:
        return len(self._content)

    def return_object(self, chosen_slot: str) -> str:
        return self._listing[int(chosen_slot)][0]


class DualContainerScreen(WindowContent):
    def __init__(self, game_object):
        super().__init__(game_object)
        self._left_data = None
        self._right_data = None
        self._left_size: tuple[int, int] = (0, 0)
        self._right_size: tuple[int, int] = (0, 0)
        self._extra_pads = {}
        self._left_name = 'left_container'
        self._right_name = 'right_container'
        self._get_container_data()
        self._active_container = self._left_name
        self._selected_pos = (0, 0)
        self._own_commands = {commands.Move(): self._move_item_focus,
                              commands.SwitchContainers(): self._switch_containers}
        self._max_view_width = config.max_text_line_length // 2

    def _get_container_data(self) -> None:
        raise NotImplementedError(f'Class {self.__class__} must implement _get_containers()!')

    def _move_item_focus(self, direction):
        raise NotImplementedError

    def _switch_containers(self, _) -> bool:
        if self._active_container is self._left_name:
            self._active_container = self._right_name
        else:
            self._active_container = self._left_name
        return True

    def _prettify_container(self, container_name: str = None, container_data: str = None,
                            container_size: tuple[int, int] = None):
        border_color = console.fg.default if container_name is self._active_container else console.fx.dim
        top_border_raw = container_name.center(max(container_size[1] + 2, len(container_name) + 2), '-')
        bottom_border_raw = '-' * len(top_border_raw)
        top_border = top_border_raw.center(self._max_view_width, ' ')
        bottom_border = bottom_border_raw.center(self._max_view_width, ' ')
        left_pad = ' ' * ((self._max_view_width - container_size[1]) // 2)
        self._extra_pads[self._active_container] = len(left_pad)
        right_pad = ' ' * (self._max_view_width - container_size[1] - len(left_pad))
        newline_replacement = right_pad + '\n' + left_pad
        padded_content = left_pad + container_data.replace('\n', newline_replacement) + right_pad
        return '\n'.join([border_color + top_border + console.fx.end,
                          padded_content,
                          border_color + bottom_border + console.fx.end])

    def data(self) -> str:
        pretty_left = self._prettify_container(self._left_name, self._left_data, self._left_size)
        pretty_right = self._prettify_container(self._right_name, self._right_data, self._right_size)
        # Add empty lines to match the two views
        extra_rows_on_the_right = len(pretty_right.split('\n')) - len(pretty_left.split('\n'))
        if extra_rows_on_the_right > 0:
            pretty_left += ('\n' + ' ' * self._max_view_width) * extra_rows_on_the_right
        else:
            pretty_right += '\n' * (-1 * extra_rows_on_the_right)
        # Combine the rows of the two
        combined_content = [''.join(pair) for pair
                            in zip(pretty_left.split('\n'), pretty_right.split('\n'))]
        return '\n'.join(combined_content)

    def cursor_pos(self) -> tuple[int, int]:
        left_pad = self._extra_pads[self._active_container]
        if self._active_container is self._right_name:
            left_pad += self._max_view_width
        return self._selected_pos[0] + 1, self._selected_pos[1] + left_pad


class MapScreen(DualContainerScreen):
    def _get_container_data(self) -> None:
        self._left_data = self.game_object.get_world_data()
        self._right_data = self.game_object.get_region_data()
        self._left_size = (config.world_size, config.world_size)
        self._right_size = (config.region_size, config.region_size)
        self._left_name = 'World'
        self._right_name = 'Region'


class InventoryScreen(DualContainerScreen):
    pass


class PagedList(WindowContent):
    def __init__(self, game_object):
        super().__init__(game_object)
        self.sorted_item_list = self._get_items()
        self._item_descriptions = [f'{console.fg.yellow}#)'
                                   f' {self._line_up(f"{item.name}: {item.description}")}'
                                   .replace(f'{item.name}:', f'{item.color + item.name}:{console.fx.end}')
                                   for number, item in enumerate(self.sorted_item_list)]
        description_lines = [len(desc.split('\n')) for desc in self._item_descriptions]
        self._pages = self._paginate(description_lines)
        self._current_page = 0

    def _get_items(self) -> list:
        raise NotImplementedError(f'Class {self.__class__} must implement _get_items()!')

    def commands(self) -> dict:
        if len(self._pages) > 1:
            return {commands.NextPage(): self._next_page,
                    commands.PreviousPage(): self._previous_page}
        return {}

    def _next_page(self, _):
        self._current_page = min(self._current_page + 1, len(self._pages) - 1)

    def _previous_page(self, _):
        self._current_page = max(self._current_page - 1, 0)

    def return_object(self, object_number_in_page_as_string: str):
        absolute_object_number = self._pages[self._current_page][0] + int(object_number_in_page_as_string)
        return self.sorted_item_list[absolute_object_number]

    def _current_page_content(self) -> list[str]:
        if not self.sorted_item_list:
            return ['There is no suitable item to use here.']
        curr_start, curr_end = self._pages[self._current_page]
        return self._item_descriptions[curr_start:curr_end]

    def data(self) -> str:
        contents = self._current_page_content()
        final_contents = [content.replace('#)', f'{n})') for content, n
                          in zip(contents, range(len(contents)))]
        if len(self._pages) > 1:
            hint_line = ' ' * config.max_text_line_length
            if self._current_page < len(self._pages) - 1:
                hint = commands.NextPage.hint
                hint_line = hint_line[:-1 * len(hint)] + hint
            if self._current_page > 0:
                hint = commands.PreviousPage.hint
                hint_line = hint + hint_line[len(hint):]
            final_contents = final_contents + [hint_line]
        return '\n'.join(final_contents)

    @staticmethod
    def _paginate(contents) -> [(int, int)]:
        # TODO: Write a test for the 10 lines rule!
        pages = []
        current_size = 0
        current_start_index = 0
        for i, content in enumerate(contents):
            if current_size + content > config.max_text_lines_on_page \
                    or i - current_start_index > 9:
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
        if self.sorted_item_list:
            return len(self._current_page_content())
        else:
            return 0

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


class SentientSpeciesList(PagedList):
    def _get_items(self) -> list:
        return sorted(self.game_object.races, key=lambda x: x.sort_key)


class EquipmentList(PagedList):
    def _get_items(self) -> list:
        return sorted(self.game_object.get_available_equipment(), key=lambda x: x.sort_key)


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
