import logging
import pathlib
import os
from typing import Tuple

logger = logging.getLogger(__name__)
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))


class SpineResponse(object):

    def __init__(self):
        self.response_file_location = None
        self.response_code = 200

    def override_response(self, response_file_location: str):
        self.response_file_location = response_file_location
        return self

    def override_response_code(self, response_code: int):
        self.response_code = response_code
        return self

    def get_response(self) -> Tuple[int, str]:
        response_from_file = pathlib.Path(ROOT_DIR) / "configured_responses" / self.response_file_location
        return self.response_code, response_from_file.read_text()


class SpineMultiResponse(object):
    """A class to control the response returned to the MHS depending on how many calls have been made previously"""

    def __init__(self):
        self.responses = []
        self.current_response_count = 0

    def with_ordered_response(self, response: SpineResponse):
        """
        Appends a given `SpineResponse` to the list, the order of the response list reflects the order in which
        this method was called
        :param response: A pre-configured SpineResponse instance
        :return: self
        """
        self.responses.append(response)
        return self

    def get_response(self) -> Tuple[int, str]:
        """
        Gets the response of the next `SpineResponse` object in the list, if the final response in the list has been
        reached, the count will reset to the first
        :return: The next `SpineResponse`
        """
        response = self.responses[self.current_response_count]
        self.current_response_count = (self.current_response_count + 1) % len(self.responses)
        return response.get_response()
