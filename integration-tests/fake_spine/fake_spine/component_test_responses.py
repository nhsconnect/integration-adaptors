from typing import List

from fake_spine.request_matcher_wrappers import ebxml_body_contains_message_id, body_contains_message_id
from fake_spine.request_matching import MatcherAndResponses, RequestMatcher
from fake_spine.spine_responses import SpineResponseBuilder, SpineMultiResponse


def _match_message_id_in_ebxml(unique_identifier: str, message_id: str) -> RequestMatcher:
    return RequestMatcher(unique_identifier, lambda x: ebxml_body_contains_message_id(x.body.decode(), message_id))


def _match_message_id_in_soap(unique_identifier: str, message_id: str) -> RequestMatcher:
    return RequestMatcher(unique_identifier, lambda x: body_contains_message_id(x.body.decode(), message_id))


def component_test_responses() -> List[MatcherAndResponses]:
    soap_fault_response = SpineResponseBuilder().override_response_code(500).override_response('soap_fault_single_error.xml')
    ebxml_fault_response = SpineResponseBuilder().override_response_code(500).override_response('ebxml_fault_single_error.xml')
    async_reliable_success = SpineResponseBuilder().override_response('async_reliable_success_response.xml')
    retriable_soap_fault = SpineResponseBuilder().override_response_code(500).override_response('soap_fault_that_should_be_retried.xml')

    response_mappings = []

    response_mappings.append(MatcherAndResponses(
        _match_message_id_in_ebxml('soap-fault-response', 'AD7D39A8-1B6C-4520-8367-6B7BEBD7B842'),
        soap_fault_response
    ))

    response_mappings.append(MatcherAndResponses(
        _match_message_id_in_soap('soap-fault-response', 'F5187FB6-B033-4A75-838B-9E7A1AFB3111'),
        soap_fault_response
    ))

    response_mappings.append(MatcherAndResponses(
        _match_message_id_in_ebxml('exml-fault-response', '7AA57E38-8B20-4AE0-9E73-B9B0C0C42BDA'),
        ebxml_fault_response
    ))

    response_mappings.append(MatcherAndResponses(
        _match_message_id_in_ebxml('async-reliable-retry-response', '35586865-45B0-41A5-98F6-817CA6F1F5EF'),
        SpineMultiResponse()
            .with_ordered_response(retriable_soap_fault)
            .with_ordered_response(retriable_soap_fault)
            .with_ordered_response(async_reliable_success)
    ))

    response_mappings.append(MatcherAndResponses(
        _match_message_id_in_ebxml('async-reliable-ebxml-fault', 'A7D43B03-38FB-4ED7-8D04-0496DBDEDB7D'),
        ebxml_fault_response
    ))

    response_mappings.append(MatcherAndResponses(
        _match_message_id_in_ebxml('async-reliable-soap-fault', '3771F30C-A231-4D64-A46C-E7FB0D52C27C'),
        soap_fault_response
    ))

    response_mappings.append(MatcherAndResponses(
        _match_message_id_in_ebxml('forward-reliable-retry-response', '96A8F79D-194D-4DCA-8D6E-6EDDC6A29F3F'),
        SpineMultiResponse()
            .with_ordered_response(retriable_soap_fault)
            .with_ordered_response(retriable_soap_fault)
            .with_ordered_response(async_reliable_success)
    ))

    return response_mappings