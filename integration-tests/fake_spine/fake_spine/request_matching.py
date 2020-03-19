import logging
from typing import Callable, List, Tuple
from tornado.httputil import HTTPServerRequest
from fake_spine.spine_response import SpineResponse
from typing import NamedTuple

logger = logging.getLogger(__name__)


class RequestMatcher(object):

    def __init__(self, unique_identifier: str, matcher: Callable[[HTTPServerRequest], bool]):
        self.matcher = matcher
        self.unique_identifier = unique_identifier

    def does_match(self, request: HTTPServerRequest) -> bool:
        return self.matcher(request)


class MatcherAndResponse(NamedTuple):
    request_matcher: RequestMatcher
    response: SpineResponse


class SpineRequestResponseMapper(object):

    def __init__(self, request_matcher_to_response: List[MatcherAndResponse]):
        """
        :param request_matcher_to_response: An ordered list of matchers and response
        """
        self.request_matcher_to_response = request_matcher_to_response

    def response_for_request(self, request: HTTPServerRequest) -> Tuple[int, str]:
        for request_matcher, response in self.request_matcher_to_response:
            try:
                matches_response = request_matcher.does_match(request)
                if matches_response:
                    logger.info(f'request matched a configured matcher: {request_matcher.unique_identifier}')
                    return response.get_response()
            except Exception as e:
                logger.warning(f'Matcher threw exception: {e}')

        logger.exception(f'No matcher configured that matched the request.\nHEADERS{request.headers}\nBODY{request.body.decode()}')
        raise Exception(f'No matcher configured that matched the request.')
