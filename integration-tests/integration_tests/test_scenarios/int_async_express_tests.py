from unittest import TestCase

from integration_tests.helpers import methods, message_retriever
import xml.etree.ElementTree as ET
import asyncio
import concurrent
from concurrent.futures import ProcessPoolExecutor
from utilities.test_utilities import async_test

class FunctionalTest(TestCase):

    def test_async_express_outbound_status(self):
        # the response is just an acknowledgement from spine...
        outbound_response, _, _ = methods.get_interaction_from_template('async express',
                                                                        'QUPC_IN160101UK05',
                                                                        '9689177621',
                                                                        'Asynchronous Express test',
                                                                        sync_async=False)

        # we need to 'accept' the message in the queue, so it is removed and doesn't impact on subsequent tests
        message_retriever.get_inbound_response()
        self.assertTrue(methods.check_status_code(outbound_response, 202),
                        "Async Express outbound test failed")

    def test_async_express_inbound_message_id(self):
        # send the message
        outbound_response, sent_message_id, _ = methods.get_interaction_from_template('async express',
                                                                                      'QUPC_IN160101UK05',
                                                                                      '9689177699',
                                                                                      'Asynchronous Express test',
                                                                                      pass_message_id=True,
                                                                                      pass_correlation_id=False)
        # then retrieve the message Id for the response (from the queue)...
        received_message_id, _, _ = message_retriever.get_inbound_response()
        self.assertEqual(received_message_id, sent_message_id,
                         "Async Express inbound message Id test failed")

    def test_async_express_inbound_correlation_id(self):
        # send the message
        outbound_response, _, sent_correlation_id = methods.get_interaction_from_template('async express',
                                                                                          'QUPC_IN160101UK05',
                                                                                          '9689177710',
                                                                                          'Asynchronous Express test',
                                                                                          pass_message_id=False,
                                                                                          pass_correlation_id=True)
        # then retrieve the correlation Id for the response (from the queue)...
        _, received_correlation_id, _ = message_retriever.get_inbound_response()
        self.assertEqual(received_correlation_id, sent_correlation_id,
                         "Async Express inbound correlation Id test failed")

    def test_async_express_inbound_response(self):
        # send the message
        methods.get_interaction_from_template('async express',
                                              'QUPC_IN160101UK05',
                                              '9689177869',
                                              'Asynchronous Express test')
        # then retrieve the response from the queue...
        _, _, inbound_response = message_retriever.get_inbound_response()
        self.assertTrue(methods.check_response(inbound_response, 'queryResponseCode'),
                        "Async Express inbound response test failed")

    def test_async_express_inbound_patient(self):
        # send the message
        methods.get_interaction_from_template('async express',
                                              'QUPC_IN160101UK05',
                                              '9689177923',
                                              'Asynchronous Express test')
        # then retrieve the response from the queue...
        _, _, inbound_response = message_retriever.get_inbound_response()
        patient_number = methods.get_section(inbound_response, 'extension', 'id', 'patient')
        self.assertEqual(patient_number, '9689177923',
                         "Async Express inbound response test failed")


class TestSyncAsyncWrapper(TestCase):

    def test_async_express_sync_async_wrap(self):
        outbound_response, _, _ = methods.get_interaction_from_template('async express',
                                                                        'QUPC_IN160101UK05',
                                                                        '9689177621',
                                                                        'Asynchronous Express test',
                                                                        sync_async=True)
        self.assertTrue(methods.check_status_code(outbound_response, 200),
                        "Async Express outbound test failed")

        root = ET.ElementTree(ET.fromstring(outbound_response.text)).getroot()
        element = root.find('.//hl7:queryResponseCode', namespaces={'hl7': 'urn:hl7-org:v3'})
        self.assertEqual('OK', element.attrib['code'])

    @async_test
    async def test_async_small_soak(self):
        loop = asyncio.get_event_loop()
        executor = concurrent.futures.ThreadPoolExecutor(max_workers=5)
        await asyncio.gather(*[loop.run_in_executor(executor, self._make_call_assert_response, f'968917762{i}') for i in range(5)])

    def _make_call_assert_response(self, nhs_id):
        result, _, _ = methods.get_interaction_from_template('async express',
                                                             'QUPC_IN160101UK05',
                                                             nhs_id,
                                                             'Asynchronous Express test',
                                                             sync_async=True)
        self.assertEqual(result.status_code, 200)
