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
