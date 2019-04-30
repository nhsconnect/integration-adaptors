LF = "\n"


class FileUtilities:
    @staticmethod
    def get_file_string(file_path):
        """Gets the contents of a string from a file.

        :param file_path: The file to load the string from.
        :return: string containing the file data.
        """
        with open(file_path) as file:
            return file.read()

    @staticmethod
    def normalize_line_endings(string_to_normalize):
        """Normalize the line endings of a string

        :param string_to_normalize: The string to be normalized.
        :return: A normalized version of the provided string.
        """
        lines = string_to_normalize.splitlines()
        normalized_string = LF.join(lines)
        return normalized_string
