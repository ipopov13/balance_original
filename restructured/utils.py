import re

strip_sub = re.compile(r"""
    \x1b     # literal ESC
    \[       # literal [
    [;\d]*   # zero or more digits or semicolons
    [A-Za-z] # a letter
    """, re.VERBOSE).sub


def strip_ansi_escape_sequences(colored_string):
    return strip_sub("", colored_string)


def horizontal_pad(content_data: str, max_width: int, pad_character: str = ' '):
    """
    Center a multiline string using the the longest content line
    """
    raw_content_data = strip_ansi_escape_sequences(content_data)
    raw_content_data = raw_content_data.split('\n')
    content_data = content_data.split('\n')
    longest_line_len = max([len(line) for line in raw_content_data])
    left_pad = (max_width - longest_line_len) // 2
    min_right_pad = max_width
    for row_index in range(len(content_data)):
        content_data[row_index] = pad_character * left_pad + content_data[row_index]
    for row_index in range(len(content_data)):
        right_pad = (max_width - len(raw_content_data[row_index]))
        content_data[row_index] += pad_character * right_pad
        min_right_pad = min(right_pad, min_right_pad)
    return content_data, left_pad, min_right_pad
