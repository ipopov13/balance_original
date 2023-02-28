import commands
import config
import console
import utils


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


class EndedGameContent(WindowContent):
    def data(self) -> str:
        return self.game_object.game_over_screen()


class CharacterSheet(WindowContent):
    def __init__(self, game_object):
        super().__init__(game_object)
        self.creature = self.game_object.character
        self._stats: dict[str, str] = self.creature.get_stats_data()
        self._modifiers: dict[str, str] = self.creature.get_modifier_data()
        self._resistances_and_affinities: dict[str, str] = self.creature.get_resistances_and_affinities_data()
        self._secondary_stats: dict[str, int] = self.creature.get_secondary_stats_data()
        self._skills: dict[str, int] = self._format_creature_skills()
        self._content: list[str] = []
        self._skill_pages: list[list[str]] = []
        self._current_page = 0
        self._prepare_data()

    def _format_creature_skills(self) -> dict[str, int]:
        raw_skills = self.creature.get_skills_data()
        colored_skills = {}
        for skill, value in raw_skills.items():
            try:
                skill_type, skill_name = skill.split(config.skill_delimiter)
            except ValueError:
                raise ValueError(f"Skill name {skill} does not have the prefix+delimiter+name structure!")
            color = config.skill_colors.get(skill_type, console.fg.default)
            colored_skills[color + skill_name + console.fx.end] = value
        return colored_skills

    @property
    def _own_commands(self) -> dict:
        if len(self._skill_pages) > 1:
            return {commands.NextPage(): self._next_page,
                    commands.PreviousPage(): self._previous_page}
        return {}

    def _next_page(self, _):
        self._current_page = min(self._current_page + 1, len(self._skill_pages) - 1)

    def _previous_page(self, _):
        self._current_page = max(self._current_page - 1, 0)

    def _prepare_data(self) -> None:
        character_name = utils.center_ansi_multiline([f"{self.creature.name} the {self.creature.species.name}"])
        self._content = character_name + [' ' * config.max_text_line_length]
        justified_stats = utils.justify_ansi_dict(self._stats)
        justified_secondary_stats = utils.justify_ansi_dict(self._secondary_stats)
        stats_width = utils.raw_length(justified_stats[0]) + utils.raw_length(justified_secondary_stats[0])
        race_desc = utils.text_to_multiline(self.creature.species.description,
                                            line_limit=config.max_text_line_length - stats_width - 2).split('\n')
        equalized_content = utils.equalize_rows([justified_stats, justified_secondary_stats, race_desc])
        stats_and_race = ['  '.join(rows) for rows in zip(*[c for c in equalized_content])]
        self._content += stats_and_race + [' ' * config.max_text_line_length]

        modifier_title = 'Modifiers'
        if self._modifiers:
            adjusted_modifiers = utils.justify_ansi_dict(self._modifiers)
        else:
            adjusted_modifiers = ["No modifiers"]
        if len(modifier_title) > utils.raw_length(adjusted_modifiers[0]):
            adjusted_modifiers = utils.center_ansi_multiline(adjusted_modifiers, len(modifier_title))
        else:
            modifier_title = modifier_title.center(utils.raw_length(adjusted_modifiers[0]))
        modifier_content = utils.center_ansi_multiline([modifier_title] + adjusted_modifiers,
                                                       config.max_text_line_length // 2)
        resistances_title = 'Resistances/Affinities'
        if self._resistances_and_affinities:
            adjusted_resistances = utils.justify_ansi_dict(self._resistances_and_affinities)
        else:
            adjusted_resistances = ["No resistances or affinities"]
        if len(resistances_title) > utils.raw_length(adjusted_resistances[0]):
            adjusted_resistances = utils.center_ansi_multiline(adjusted_resistances, len(resistances_title))
        else:
            resistances_title = resistances_title.center(utils.raw_length(adjusted_resistances[0]))
        resistances_content = utils.center_ansi_multiline([resistances_title] + adjusted_resistances,
                                                          config.max_text_line_length // 2)
        equalized_content = utils.equalize_rows([modifier_content, resistances_content])
        mod_and_res = ['  '.join(rows) for rows in zip(*[c for c in equalized_content])]
        self._content += mod_and_res

        self._content += [' ' * config.max_text_line_length] +\
                         ["Skills".center(config.max_text_line_length)] +\
                         [' ' * config.max_text_line_length]
        available_rows = config.max_text_lines_on_page - len(self._content)
        if self._skills:
            self._skill_pages = utils.columnize(self._skills, rows=available_rows, fill_all_rows=True)
        else:
            self._skill_pages = [["You don't have any discernible skills yet.".center(config.max_text_line_length)]]

    def data(self) -> str:
        return '\n'.join(self._content + self._skill_pages[self._current_page])


class GameScene(WindowContent):
    def data(self) -> str:
        character_hud = self.game_object.get_character_hud()
        area_view = self.game_object.get_area_view()
        self.game_object.sub_turn_tick()
        return '\n'.join([area_view, character_hud])

    def cursor_pos(self) -> tuple[int, int]:
        return self.game_object.get_cursor_position_in_location()


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
        return {commands.Select(): self._move_item_focus,
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
        new_selection = utils.calculate_new_position(self._selected_pos[self._active_container_index], direction,
                                                     *self._container_sizes[self._active_container_index])
        self._selected_pos[self._active_container_index] = new_selection
        self._get_container_data()
        return True

    def _switch_containers(self, _) -> bool:
        self._active_container_index += 1
        if self._active_container_index == len(self._names):
            self._active_container_index = 0
        return True

    def _prettify_container(self, container_index: int = None) -> list[str]:
        container_data = self._data[container_index].split('\n')
        border_color = console.fg.default if container_index is self._active_container_index else console.fx.dim
        name = self._names[container_index]
        longest_line = utils.longest_raw_line_len(container_data)
        top_border_raw = name.center(max(longest_line + 2, len(name) + 2), '-')
        bottom_border_raw = '-' * len(top_border_raw)
        padded_data, inner_left_pad, _ = utils.left_justify_ansi_multiline(container_data, len(top_border_raw))
        content_data = ([border_color + top_border_raw + console.fx.end]
                        + padded_data
                        + [border_color + bottom_border_raw + console.fx.end])
        content_data, left_pad, _ = utils.left_justify_ansi_multiline(content_data, self._max_view_width)
        self._extra_pads[container_index] = left_pad + inner_left_pad
        final_content = content_data + [' ' * self._max_view_width]
        return final_content

    def data(self) -> str:
        pretty_content = [self._prettify_container(ci) for ci in range(len(self._names))]
        details = [utils.left_justify_ansi_multiline(det, self._max_view_width)[0] for det in self._get_details()]
        pretty_content = [c + d for c, d in zip(pretty_content, details)]
        equalized_content = utils.equalize_rows(pretty_content, self._max_view_width)
        combined_content = [''.join(rows) for rows in zip(*[c for c in equalized_content])]
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
        object_state = self.game_object.active_inventory_container_name
        if object_state in self._names:
            self._active_container_index = self._names.index(object_state)
        if object_state is config.equipment_title:
            self._selected_pos[2] = (self.game_object.selected_equipped_item_index,
                                     self._selected_pos[2][1])

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
        equip_details = self.game_object.get_equipped_item_details(self._selected_pos[2])
        return ground_details, bag_details, equip_details

    def _decorate_callback(self, callback):
        """
        We decorate game_object methods so that we don't have to reload the window after we call them
        """
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
                                   f' {utils.text_to_multiline(f"{item.name}: {item.description}")}'
                                   .replace('\n', '\n   ')
                                   .replace(f'{item.name}:', f'{item.color + item.name}:{console.fx.end}')
                                   for number, item in enumerate(self.sorted_item_list)]
        description_lines = [len(desc.split('\n')) for desc in self._item_descriptions]
        self._pages = self._paginate(description_lines)
        self._current_page = 0
        self._empty_list_message = 'There is no suitable item to use here.'

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
            return [self._empty_list_message]
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


class SentientSpeciesList(PagedList):
    def _get_items(self) -> list:
        return sorted(self.game_object.races, key=lambda x: x.sort_key)


class EquipmentList(PagedList):
    def _get_items(self) -> list:
        return sorted(self.game_object.get_available_equipment(), key=lambda x: x.sort_key)


class SubstancesList(PagedList):
    def __init__(self, game_object):
        super().__init__(game_object)
        self._empty_list_message = 'No matching liquids found.'

    def _get_items(self) -> list:
        return sorted(self.game_object.get_available_substances(), key=lambda x: x.sort_key)


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
