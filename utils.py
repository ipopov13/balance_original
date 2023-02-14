import re
from typing import Union

import console
import config

strip_sub = re.compile(r"""
    \x1b     # literal ESC
    \[       # literal [
    [;\d]*   # zero or more digits or semicolons
    [A-Za-z] # a letter
    """, re.VERBOSE).sub


def strip_ansi_escape_sequences(colored_string: str) -> str:
    return strip_sub("", colored_string)


def raw_length(colored_string: str) -> int:
    return len(strip_ansi_escape_sequences(colored_string))


def longest_raw_line_len(content) -> int:
    raw_content_data = [strip_ansi_escape_sequences(line) for line in content]
    longest_line_len = max([len(line) for line in raw_content_data])
    return longest_line_len


def dim(a_string) -> str:
    return console.fx.dim + a_string + console.fx.end


def equalize_rows(contents: list[list[str]], fixed_width: int = None) -> list[list[str]]:
    max_lines = max([len(content) for content in contents])
    for content in contents:
        line_width = fixed_width or max([raw_length(line) for line in content])
        current_height = len(content)
        content += [' ' * line_width] * max(0, max_lines - current_height)
    return contents


def left_justify_ansi_multiline(content_data: list[str], max_width: int, pad_character: str = ' ') \
        -> tuple[list[str], int, int]:
    """
    Left-justify a multiline string using the longest content line
    """
    longest_line_len = max([raw_length(line) for line in content_data])
    left_pad = (max_width - longest_line_len) // 2
    justified_content = []
    min_right_pad = max_width
    for line in content_data:
        right_pad = max_width - raw_length(line) - left_pad
        min_right_pad = min(right_pad, min_right_pad)
        justified_line = (pad_character * left_pad) + line + (pad_character * right_pad)
        justified_content.append(justified_line)
    return justified_content, left_pad, min_right_pad


def center_ansi_multiline(content_data: list[str], max_width: int = config.max_text_line_length,
                          pad_character: str = ' ') -> list[str]:
    """
    Center a multiline string using the longest content line
    """
    centered_content = []
    for line in content_data:
        raw_len = raw_length(line)
        left_pad = (max_width - raw_len) // 2
        right_pad = max_width - raw_len - left_pad
        if right_pad < 0:
            raise ValueError(f"String is too long to center in {max_width} characters:\n{line}")
        centered_content.append((pad_character * left_pad) + line + (pad_character * right_pad))
    return centered_content


def columnize(data_dict: dict[str, int], rows: int, max_width: int = config.max_text_line_length,
              fill_all_rows: bool = False) -> list[list[str]]:
    dicts = [{k: data_dict[k] for k in list(data_dict.keys())[start:start + rows]}
             for start in range(0, len(data_dict), rows)]
    strips = [justify_ansi_dict(d, rows_needed=rows if fill_all_rows else None) for d in dicts]
    pages = []
    while strips:
        remaining_width = max_width
        current_page = []
        while strips and remaining_width >= raw_length(strips[0][0]):
            remaining_width -= raw_length(strips[0][0]) + 1
            current_page.append(strips.pop(0))
        pages.append(current_page)
    pages = [equalize_rows(page) for page in pages]
    combined_pages = [['|'.join(rows) for rows in zip(*[c for c in page])] for page in pages]
    return combined_pages


def justify_ansi_dict(data_dict: dict[str, Union[int, str]], rows_needed: int = None) -> list[str]:
    if not data_dict:
        return []
    max_key_len = max([raw_length(key) for key in data_dict])
    max_value_len = max([raw_length(str(value)) for value in data_dict.values()])
    max_len = max_value_len + max_key_len + 1
    content = []
    for key, value in data_dict.items():
        current_len = raw_length(key) + raw_length(str(value))
        padding = ' ' * (max_len - current_len)
        content.append(f"{key}{padding}{value}")
    if rows_needed is not None and len(content) < rows_needed:
        extra_rows = [' ' * max_len] * (rows_needed - len(content))
        content += extra_rows
    return content


def calculate_new_position(old_pos: tuple[int, int], direction: str,
                           max_row: int, max_column: int) -> tuple[int, int]:
    row, column = old_pos
    if direction in '789':
        row -= 1
        if row == -1:
            row = max_row - 1
    elif direction in '123':
        row += 1
        if row == max_row:
            row = 0
    if direction in '147':
        column -= 1
        if column == -1:
            column = max_column - 1
    elif direction in '369':
        column += 1
        if column == max_column:
            column = 0
    return row, column


def coord_distance(coords1: tuple[int, int], coords2: tuple[int, int]) -> int:
    return max(abs(coords1[0] - coords2[0]), abs(coords1[1] - coords2[1]))


def cmp(a: int, b: int) -> int:
    """Return -1 if a < b, 0 if a == b, and 1 if a > b"""
    if a < b:
        return -1
    elif a > b:
        return 1
    else:
        return 0


def direct_path(a: tuple[int, int], b: tuple[int, int]) -> list[tuple[int, int]]:
    path = [a[:]]
    dif = [abs(a[0] - b[0]), abs(a[1] - b[1])]
    direction_steps = [0, 0]
    if abs(a[0] - b[0]):
        direction_steps[0] = (b[0] - a[0]) // abs(a[0] - b[0])
    if abs(a[1] - b[1]):
        direction_steps[1] = (b[1] - a[1]) // abs(a[1] - b[1])
    longer = dif.index(max(dif))
    shorter = [1, 0][longer]
    if dif[longer]:
        floater = float(dif[shorter]) / dif[longer]
    else:
        return [a, b]
    for x in range(dif[longer]):
        point = list(a)
        point[longer] += (x + 1) * direction_steps[longer]
        point[shorter] += int(round((x + 1) * floater)) * direction_steps[shorter]
        path.append(tuple(point))
    return path


def make_stats(default: int = 1, stats: dict[str, int] = None) -> dict[str, int]:
    if stats is None:
        stats = {}
    stats = {stat: stats.get(stat, default) for stat in config.stats_order}
    return stats


def text_to_multiline(text: str, line_limit: int = config.max_text_line_length) -> str:
    """Turn the text into a multiline string"""
    lines = []
    text = text.strip()
    while text:
        if len(text) > line_limit:
            a_line = text[:line_limit].rsplit(' ', 1)[0]
        else:
            a_line = text
        lines.append(a_line.strip())
        text = text[len(a_line):].strip()
    return '\n'.join(lines)


def add_dicts(dict1: dict[str, int], dict2: dict[str, int]) -> dict[str, int]:
    new_dict = dict1.copy()
    for key, value in dict2.items():
        new_dict[key] = new_dict.get(key, 0) + value
    return new_dict


def multiply_and_append_dict(base: dict[str, float], addition: dict[str, float]) -> dict[str, float]:
    new_dict = base.copy()
    for key, value in addition.items():
        new_dict[key] = new_dict.get(key, 1) * value
    return new_dict


if __name__ == "__main__":
    test = {i: i+1 for i in range(13)}
    print(columnize(test, 5))
