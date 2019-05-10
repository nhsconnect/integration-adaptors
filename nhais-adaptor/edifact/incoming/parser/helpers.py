from typing import List
from edifact.incoming.parser import EdifactDict


def extract_relevant_lines(original_dict: EdifactDict, starting_pos: int, terminator_keys: List[str]) -> EdifactDict:
    """
    From the original dict generate a smaller dict just containing the relevant lines from the starting_pos
    to when then terminator_keys is found
    :param original_dict: The original larger dictionary.
    :param starting_pos: The starting position to start the loop from.
    This is to prevent starting the loop from the start each time and be slightly more efficient.
    :param terminator_keys: a list of terminator keys that signal when all the relevant lines have been found
    :return: A smaller dictionary with just the relevant lines for the section.
    """
    new_dict = EdifactDict([])
    for (key, value) in original_dict[starting_pos:]:
        if key not in terminator_keys:
            new_dict.append((key, value))
        else:
            break

    return new_dict


def convert_to_dict(lines: List[str]) -> EdifactDict:
    """
    Takes the list of original edifact lines and converts to a dict.
    :param lines: a list of string of the original edifact lines.
    :return: EdifactDict - A list of Tuples. Since the keys in the edifact interchange can
    contain duplicates a tuple is required here rather than a set.
    """
    generated_dict = EdifactDict([])

    for line in lines:
        key_value = line.split("+", 1)
        generated_dict.append((key_value[0], key_value[1]))

    return generated_dict
