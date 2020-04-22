from typing import List

from fake_spine import vnp_request_matcher_wrappers
from fake_spine.request_matching import MatcherAndResponses
from fake_spine.vnp_spine_response import VnpSpineResponseBuilder

ASYNC_EXPRESS_INBOUND_HEADERS = {
    'Soapaction': 'urn:nhs:names:services:psisquery/QUPC_IN160102UK05'
}


def vnp_test_responses() -> List[MatcherAndResponses]:
    response_mappings = []

    response_mappings.append(MatcherAndResponses(
        vnp_request_matcher_wrappers.async_express(),
        VnpSpineResponseBuilder().override_inbound_request('async_express_inbound')
                                 .override_inbound_request_headers(ASYNC_EXPRESS_INBOUND_HEADERS)
    ))

    response_mappings.append(MatcherAndResponses(
        vnp_request_matcher_wrappers.async_reliable(),
        VnpSpineResponseBuilder().override_response('async_reliable_outbound_response')
                                 .override_inbound_request('async_reliable_inbound')
    ))

    response_mappings.append(MatcherAndResponses(
        vnp_request_matcher_wrappers.sync(),
        VnpSpineResponseBuilder().override_response('sync_outbound_response')
                                 .override_response_code(200)
    ))

    response_mappings.append(MatcherAndResponses(
        vnp_request_matcher_wrappers.forward_reliable(),
        VnpSpineResponseBuilder().override_response('async_reliable_outbound_response')
                                 .override_inbound_request('async_reliable_inbound')
    ))

    return response_mappings