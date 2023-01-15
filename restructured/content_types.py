import commands
import config
import console
from utils import horizontal_pad, calculate_new_position, longest_raw_line_len


class WindowContent:
    def __init__(self, game_object):
        self.game_object = game_object

    @property
    def _own_commands(self):
        return {}

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
        equipment = self.game_object.get_equipment_list()
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


class MultiContainerScreen(WindowContent):
    def __init__(self, game_object):
        super().__init__(game_object)
        self._names: list[str] = []
        self._set_names()
        self._data = []
        self._container_sizes: list[tuple[int, int]] = []
        self._selected_pos = self._get_initial_selected_position()
        self._get_container_data()
        self._extra_pads = [0] * len(self._names)
        self._active_container_index: int = 0
        self._max_view_width = config.location_width // len(self._names)

    @property
    def _own_commands(self):
        return {commands.Move(): self._move_item_focus,
                commands.SwitchContainers(): self._switch_containers}

    def _get_initial_selected_position(self) -> list[tuple[int, int]]:
        return [(0, 0)] * len(self._names)

    def _set_names(self) -> None:
        raise NotImplementedError(f'Class {self.__class__} must implement _set_names()!')

    def _get_container_data(self) -> None:
        raise NotImplementedError(f'Class {self.__class__} must implement _get_containers()!')

    def _get_details(self) -> tuple[list[str], list[str]]:
        raise NotImplementedError(f'Class {self.__class__} must implement _get_details()!')

    def _move_item_focus(self, direction) -> bool:
        new_selection = calculate_new_position(self._selected_pos[self._active_container_index], direction,
                                               *self._container_sizes[self._active_container_index])
        self._selected_pos[self._active_container_index] = new_selection
        self._get_container_data()
        return True

    def _switch_containers(self, _) -> bool:
        self._active_container_index += 1
        if self._active_container_index == len(self._names):
            self._active_container_index = 0
        return True

    def _prettify_container(self, container_index: int = None):
        container_data = self._data[container_index].split('\n')
        border_color = console.fg.default if container_index is self._active_container_index else console.fx.dim
        name = self._names[container_index]
        longest_line = longest_raw_line_len(container_data)
        top_border_raw = name.center(max(longest_line + 2, len(name) + 2), '-')
        bottom_border_raw = '-' * len(top_border_raw)
        padded_data, inner_left_pad, _ = horizontal_pad(container_data, len(top_border_raw))
        content_data = ([border_color + top_border_raw + console.fx.end]
                        + padded_data
                        + [border_color + bottom_border_raw + console.fx.end])
        content_data, left_pad, _ = horizontal_pad(content_data, self._max_view_width)
        self._extra_pads[container_index] = left_pad + inner_left_pad
        final_content = '\n'.join(content_data) + self._empty_row() + '\n'
        return final_content

    def _empty_row(self) -> str:
        return '\n' + ' ' * self._max_view_width

    def _equalize_rows(self, contents):
        max_lines = max([len(content.split('\n')) for content in contents])
        for c_i in range(len(contents)):
            current_height = len(contents[c_i].split('\n'))
            contents[c_i] += self._empty_row() * max(0, max_lines - current_height)
        return contents

    def data(self) -> str:
        pretty_content = [self._prettify_container(ci) for ci in range(len(self._names))]
        details = [horizontal_pad(det, self._max_view_width)[0] for det in self._get_details()]
        pretty_content = [c + '\n'.join(d) for c, d in zip(pretty_content, details)]
        equalized_content = self._equalize_rows(pretty_content)
        combined_content = [''.join(rows) for rows
                            in zip(*[c.split('\n') for c in equalized_content])]
        return '\n'.join(combined_content)

    def cursor_pos(self) -> tuple[int, int]:
        left_pad = self._extra_pads[self._active_container_index]
        left_pad += self._max_view_width * self._active_container_index
        return (self._selected_pos[self._active_container_index][0] + 1,
                self._selected_pos[self._active_container_index][1] + left_pad)


class MapScreen(MultiContainerScreen):
    def _set_names(self) -> None:
        self._names = ['World', 'Region']

    def _get_initial_selected_position(self) -> list[tuple[int, int]]:
        return [self.game_object.get_character_position_in_world(),
                self.game_object.get_character_position_in_region()]

    def _get_container_data(self) -> None:
        self._data = [self.game_object.get_world_data(blink_at=self._selected_pos[0]),
                      self.game_object.get_region_data(self._selected_pos[0], blink_at=self._selected_pos[1])]
        self._container_sizes = [(config.world_size, config.world_size),
                                 (config.region_size, config.region_size)]

    def _get_details(self) -> tuple[list[str], list[str]]:
        region_details = self.game_object.get_region_map_details(self._selected_pos[0])
        location_details = self.game_object.get_location_map_details(self._selected_pos[0],
                                                                     self._selected_pos[1])
        return region_details, location_details


class InventoryScreen(MultiContainerScreen):
    def __init__(self, game_object):
        super().__init__(game_object)
        self.game_object.set_active_container(self._names[0])

    def _increment_container_index(self):
        self._active_container_index += 1
        if self._active_container_index == len(self._names):
            self._active_container_index = 0

    def _switch_containers(self, _) -> bool:
        self._increment_container_index()
        while self._container_sizes[self._active_container_index] == (0, 0):
            self._increment_container_index()
        self.game_object.set_active_container(self._names[self._active_container_index])
        return True

    def _set_names(self) -> None:
        self._names = [config.ground, self.game_object.get_bag_name(), config.equipment_title]

    def _get_container_data(self) -> None:
        self._data = [self.game_object.get_ground_items(), self.game_object.get_bag_items(),
                      self.game_object.get_equipment_data()]
        self._container_sizes = [(config.tile_size, config.tile_size), self.game_object.get_bag_size(),
                                 self.game_object.get_equipment_size()]

    def _get_details(self) -> tuple[list[str], list[str], list[str]]:
        ground_details = self.game_object.get_ground_item_details(self._selected_pos[0])
        bag_details = self.game_object.get_bag_item_details(self._selected_pos[1])
        return ground_details, bag_details, ['']

    def _decorate_callback(self, callback):

        def wrapper(*args, **kwargs):
            result = callback(*args, **kwargs)
            self._set_names()
            self._get_initial_selected_position()
            self._get_container_data()
            return result

        return wrapper

    def _object_commands(self) -> dict:
        """The mapping of commands&methods specific for the underlying object(s)"""
        object_commands = self.game_object.commands()
        for command, callback in object_commands.items():
            object_commands[command] = self._decorate_callback(callback)
        return object_commands


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
