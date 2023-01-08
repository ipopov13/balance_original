import re

strip_sub = re.compile(r"""
    \x1b     # literal ESC
    \[       # literal [
    [;\d]*   # zero or more digits or semicolons
    [A-Za-z] # a letter
    """, re.VERBOSE).sub


def strip_ansi_escape_sequences(colored_string):
    return strip_sub("", colored_string)


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
