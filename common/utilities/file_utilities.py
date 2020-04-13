import json

LF = "\n"


def get_file_string(file_path):
    """Gets the contents of a string from a file.

    :param file_path: The file to load the string from.
    :return: string containing the file data.
    """
    with open(file_path) as file:
        return file.read()


def get_file_dict(file_path):
    """Loads the contents of a JSON file as a dictionary.

    :param file_path: The file to load the dictionary from.
    :return: a dictionary representing the contents of the file.
    """
    with open(file_path) as json_file:
        return json.load(json_file)


def normalize_line_endings(string_to_normalize):
    """Normalize the line endings of a string

    :param string_to_normalize: The string to be normalized.
    :return: A normalized version of the provided string.
    """
    lines = string_to_normalize.splitlines()
    normalized_string = LF.join(lines)
    return normalized_string
