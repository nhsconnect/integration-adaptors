
class SchemaValidationException(Exception):

    def __init__(self, message, path):
        self.message = message
        self.path = path
