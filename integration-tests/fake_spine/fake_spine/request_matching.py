from utilities import integration_adaptors_logger as log
import traceback
from typing import Callable, List
from typing import NamedTuple

from tornado.httputil import HTTPServerRequest

from fake_spine.spine_responses import SpineResponse

logger = log.IntegrationAdaptorsLogger(__name__)


class RequestMatcher(object):

    def __init__(self, unique_identifier: str, matcher: Callable[[HTTPServerRequest], bool]):
        self.matcher = matcher
        self.unique_identifier = unique_identifier

    def does_match(self, request: HTTPServerRequest) -> bool:
        return self.matcher(request)

    def __str__(self):
        return self.unique_identifier


class MatcherAndResponses(NamedTuple):
    request_matcher: RequestMatcher
    response: SpineResponse


class SpineRequestResponseMapper(object):

    def __init__(self, request_matcher_to_response: List[MatcherAndResponses]):
        """
        :param request_matcher_to_response: An ordered list of matchers and response
        """
        self.request_matcher_to_response = request_matcher_to_response

    def response_for_request(self, request: HTTPServerRequest) -> SpineResponse:
        for request_matcher, responses in self.request_matcher_to_response:
            try:
                matches_response = request_matcher.does_match(request)
                if matches_response:
                    logger.info(f'request matched a configured matcher: {request_matcher.unique_identifier}')
                    return responses
            except Exception:
                tb = traceback.format_exc()
                logger.warning(f'Matcher threw exception: {tb}')

        logger.exception(f'No matcher configured that matched the request.\nHEADERS{request.headers}\nBODY{request.body.decode()}')
        raise Exception(f'No matcher configured that matched the request.')
