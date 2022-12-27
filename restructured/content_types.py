import commands
import config
import console


class WindowContent:
    def __init__(self, game_object):
        self.game_object = game_object

    @staticmethod
    def _own_commands():
        return {}

    def commands(self) -> dict:
        """Combine the content-specific and object-specific commands"""
        return {**self._object_commands(),
                **self._own_commands()}

    def data(self) -> str:
        return self.game_object.data()

    def _object_commands(self) -> dict:
        """The mapping of commands&methods specific for the underlying object(s)"""
        try:
            object_commands = self.game_object.commands()
        except AttributeError:
            object_commands = {}
            for obj in self.game_object:
                object_commands.update(obj.commands())
        return object_commands


class PagedList(WindowContent):
    def __init__(self, game_object):
        super().__init__(game_object)
        sorted_list = sorted(self.game_object, key=lambda x: x.sort_key)
        self._item_descriptions = [f'{console.fg.yellow}{number})'
                                   f' {self._line_up(f"{item.name}: {item.description}")}'
                                   .replace(f'{item.name}:', f'{item.color + item.name}:{console.fx.end}')
                                   for number, item in enumerate(sorted_list)]
        description_lines = [len(desc.split('\n')) for desc in self._item_descriptions]
        self._pages = self._paginate(description_lines)
        self._current_page = 0

    def commands(self) -> dict:
        # TODO: Test that the race is returned correctly from the second page
        return {commands.NextPage(): self._next_page,
                commands.PreviousPage(): self._previous_page}

    def _next_page(self, _):
        self._current_page = min(self._current_page + 1, len(self._pages) - 1)

    def _previous_page(self, _):
        self._current_page = max(self._current_page - 1, 0)

    def return_object(self, number_string):
        return self.game_object[int(number_string)]

    def _current_page_content(self):
        curr_start, curr_end = self._pages[self._current_page]
        return self._item_descriptions[curr_start:curr_end]

    def data(self) -> str:
        # TODO: Add the numbers of the list here to make them restart for each page
        return '\n'.join(self._current_page_content())

    @staticmethod
    def _paginate(contents) -> [(int, int)]:
        # TODO: Write a test for the 10 lines rule!
        pages = []
        current_size = 0
        current_start_index = 0
        for i, content in enumerate(contents):
            if current_size + content > config.max_text_lines_on_page \
                    or i - current_start_index == 10:
                pages.append((current_start_index, i))
                current_size = 0
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

    def data(self):
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

    def _remove_last_character(self):
        self._data = self._data[:-1]

    def data(self) -> str:
        return self._data
