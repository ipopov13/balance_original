import re
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


def horizontal_pad(content_data: list[str], max_width: int, pad_character: str = ' '):
    """
    Center a multiline string using the longest content line
    """
    raw_content_data = [strip_ansi_escape_sequences(line) for line in content_data]
    longest_line_len = max([len(line) for line in raw_content_data])
    left_pad = (max_width - longest_line_len) // 2
    min_right_pad = max_width
    for row_index in range(len(content_data)):
        content_data[row_index] = (pad_character * left_pad) + content_data[row_index]
    for row_index in range(len(content_data)):
        right_pad = (max_width - len(raw_content_data[row_index]) - left_pad)
        content_data[row_index] = content_data[row_index] + (pad_character * right_pad)
        min_right_pad = min(right_pad, min_right_pad)
    return content_data, left_pad, min_right_pad


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
