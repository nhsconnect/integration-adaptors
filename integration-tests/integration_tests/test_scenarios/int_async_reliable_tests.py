from unittest import TestCase
from integration_tests.helpers import methods, message_retriever, xml_parser


class FunctionalTest(TestCase):
    def test_async_reliable_outbound_status(self):
        # the response is just an acknowledgement from spine...
        outbound_response, _, _ = methods.get_interaction_from_template('async reliable',
                                                                        'REPC_IN150016UK05',
                                                                        '9689177621',
                                                                        'Asynchronous Reliable test')
        # we need to 'accept' the message in the queue, so it is removed and doesn't impact on subsequent tests
        message_retriever.get_inbound_response()
        self.assertTrue(methods.check_status_code(outbound_response, 202), "Async Reliable outbound test failed")

    def test_async_reliable_inbound_message_id(self):
        # send the message
        outbound_response, sent_message_id, _ = methods.get_interaction_from_template('async reliable',
                                                                                      'REPC_IN150016UK05',
                                                                                      '9689177699',
                                                                                      'Asynchronous Reliable test',
                                                                                      pass_message_id=True,
                                                                                      pass_correlation_id=False)
        # then retrieve the message Id for the response (from the queue)...
        received_message_id, _, _ = message_retriever.get_inbound_response()
        self.assertEqual(received_message_id, sent_message_id,
                         "Async Reliable inbound message Id test failed")

    def test_async_reliable_inbound_correlation_id(self):
        # send the message
        outbound_response, _, sent_correlation_id = methods.get_interaction_from_template('async reliable',
                                                                                          'REPC_IN150016UK05',
                                                                                          '9689177710',
                                                                                          'Asynchronous Reliable test',
                                                                                          pass_message_id=False,
                                                                                          pass_correlation_id=True)
        # then retrieve the correlation Id for the response (from the queue)...
        _, received_correlation_id, _ = message_retriever.get_inbound_response()
        self.assertEqual(received_correlation_id, sent_correlation_id,
                         "Async Reliable inbound correlation Id test failed")

    def test_async_reliable_inbound_response(self):
        # send the message
        methods.get_interaction_from_template('async reliable',
                                              'REPC_IN150016UK05',
                                              '9689177869',
                                              'Asynchronous Reliable test')
        # then retrieve the response from the queue...
        _, _, inbound_response = message_retriever.get_inbound_response()
        parser = xml_parser.XmlMessageParser()
        xml_response = parser.parse_message(inbound_response)
        xml_element = xml_response.find('.//hl7:detail', namespaces=xml_parser.NAMESPACES)
        self.assertEqual(xml_element.text, 'GP Summary upload successful', "should match")


class TestSyncAsyncWrapper(TestCase):

    def test_async_reliable_sync_async_wrap(self):
        outbound_response, _, _ = methods.get_interaction_from_template('async reliable',
                                                                        'REPC_IN150016UK05',
                                                                        '9689177869',
                                                                        'Asynchronous Reliable test',
                                                                        sync_async=True)

        self.assertTrue(methods.check_status_code(outbound_response, 200), "Async Reliable outbound test failed")

        parser = xml_parser.XmlMessageParser()
        xml_response = parser.parse_message(outbound_response.text)
        xml_element = xml_response.find('.//hl7:detail', namespaces=xml_parser.NAMESPACES)
        self.assertEqual(xml_element.text, 'GP Summary upload successful', "should match")
