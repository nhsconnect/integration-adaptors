import logging
from typing import Callable, Dict
from tornado.httputil import HTTPServerRequest
from fake_spineroutelookup.routing_response import RoutingResponse

logger = logging.getLogger(__name__)


class RequestMatcher(object):

    def __init__(self, matcher: Callable[[HTTPServerRequest], bool]):
        self.matcher = matcher

    def does_match(self, request: HTTPServerRequest) -> bool:
        return self.matcher(request)


class SpineRouteLookupRequestResponseMapper(object):

    def __init__(self, request_matcher_to_response: Dict[RequestMatcher, RoutingResponse]):
        self.request_matcher_to_response = request_matcher_to_response

    def response_for_request(self, request: HTTPServerRequest) -> dict:
        for request_matcher, response in self.request_matcher_to_response.items():
            matches_response = request_matcher.does_match(request)
            if matches_response:
                logger.log(logging.INFO, "request matched a configured matcher")
                return response.get_response()

        logger.log(logging.ERROR,
                   f"no matcher configured that matched request {request} with headers: {request.headers}")
        raise Exception(f"no response configured matching the request")
