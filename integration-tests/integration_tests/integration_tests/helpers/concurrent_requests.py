import unittest
from threading import Thread
from collections import namedtuple
from typing import List

from integration_tests.helpers.build_message import MhsMessage
from integration_tests.http.mhs_http_request_builder import MhsHttpRequestBuilder

OutboundResponse = namedtuple('OutboundResponse', 'message_id error')


def send_messages_concurrently(messages: List[MhsMessage], interaction_id, wait_for_response=True) -> List[OutboundResponse]:
    """
    Send all of the provided messages currently (multi-threaded)
    @param messages: the list of message to send
    @param interaction_id: the interaction is to use for all requests
    @param wait_for_response: if true the sync_async workflow will be used
    @return:
    """
    request_threads = []
    for message_body, message_id in messages:
        request_thread = OutboundRequestThread(message_body, message_id, interaction_id, wait_for_response=wait_for_response)
        request_thread.start()
        request_threads.append(request_thread)

    errors = []
    for thread in request_threads:
        thread.join()
        errors.append(OutboundResponse(thread.message_id, thread.error))
    return errors


def assert_all_messages_succeeded(responses: List[OutboundResponse]):
    assertor = unittest.TestCase('__init__')
    errors = [f'Request for message id {response.message_id} raised an exception: {response.error}'
              for response in responses if response.error]
    assertor.assertTrue(len(errors) == 0, f'{len(errors)} of {len(responses)} concurrent messages failed:'
                                          f'\n{errors}')


def has_errors(responses: List[OutboundResponse]) -> bool:
    return len([response for response in responses if response.error]) > 0


class OutboundRequestThread(Thread):

    def __init__(self, message_body, message_id, interaction_id, correlation_id='1', wait_for_response=True):
        Thread.__init__(self)
        self.message_body = message_body
        self.message_id = message_id
        self.interaction_id = interaction_id
        self.correlation_id = correlation_id
        self.wait_for_response = wait_for_response
        self.error = None

    def run(self):
        try:
            MhsHttpRequestBuilder() \
                .with_headers(interaction_id=self.interaction_id,
                              message_id=self.message_id,
                              wait_for_response=self.wait_for_response,
                              correlation_id=self.correlation_id) \
                .with_body(self.message_body) \
                .execute_post_expecting_success()
        except Exception as e:
            self.error = e
