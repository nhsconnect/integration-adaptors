class FileUtilities:
    @staticmethod
    def get_file_string(file_path):
        """Gets the contents of a string from a file.

        :param file_path: The file to load the string from.
        :return: string containing the file data.
        """
        with open(file_path) as file:
            return file.read()
