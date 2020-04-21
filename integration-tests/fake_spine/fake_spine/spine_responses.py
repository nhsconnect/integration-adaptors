import abc
from utilities import integration_adaptors_logger as log
import pathlib
from typing import Tuple, NamedTuple, Union

from tornado.httputil import HTTPServerRequest

from fake_spine import fake_spine_configuration

logger = log.IntegrationAdaptorsLogger(__name__)


class InboundRequest(NamedTuple):
    body: str
    headers: dict


class OutboundResponse(NamedTuple):
    status: int
    body: str


class SpineResponse(abc.ABC):

    @abc.abstractmethod
    def get_outbound_response(self, request: HTTPServerRequest) -> OutboundResponse:
        pass

    def get_inbound_request(self, request: HTTPServerRequest) -> Union[InboundRequest, None]:
        return None


class SpineResponseBuilder(SpineResponse):

    def __init__(self):
        self.response_file_location = None
        self.inbound_request_file_location = None
        self.response_code = 202
        self.config = fake_spine_configuration.FakeSpineConfiguration()

    def override_response(self, response_file_location: str):
        self.response_file_location = response_file_location
        return self

    def override_inbound_request(self, inbound_request_file_location: str):
        self.inbound_request_file_location = inbound_request_file_location
        return self

    def override_response_code(self, response_code: int):
        self.response_code = response_code
        return self

    def get_outbound_response(self, request: HTTPServerRequest) -> OutboundResponse:
        response_from_file = pathlib.Path(self.config.ROOT_DIR) / "configured_responses" / self.response_file_location
        return OutboundResponse(self.response_code, response_from_file.read_text())


class SpineMultiResponse(SpineResponse):
    """A class to control the response returned to the MHS depending on how many calls have been made previously"""

    def __init__(self):
        self.responses = []
        self.current_response_count = 0

    def with_ordered_response(self, response: SpineResponseBuilder):
        """
        Appends a given `SpineResponse` to the list, the order of the response list reflects the order in which
        this method was called
        :param response: A pre-configured SpineResponse instance
        :return: self
        """
        self.responses.append(response)
        return self

    def get_outbound_response(self, request: HTTPServerRequest) -> Tuple[int, str]:
        """
        Gets the response of the next `SpineResponse` object in the list, if the final response in the list has been
        reached, the count will reset to the first
        :return: The next `SpineResponse`
        """
        response = self.responses[self.current_response_count]
        self.current_response_count = (self.current_response_count + 1) % len(self.responses)
        return response.get_outbound_response(request)
