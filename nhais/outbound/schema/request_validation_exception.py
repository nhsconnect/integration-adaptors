import collections
from typing import List

ValidationError = collections.namedtuple('ValidationError', 'path message')


class RequestValidationException(Exception):

    def __init__(self, errors: List[ValidationError]):
        self.errors = errors
