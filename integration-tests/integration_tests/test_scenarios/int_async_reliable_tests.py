from unittest import TestCase, skip

import integration_tests.helpers


class FunctionalTest(TestCase):
    def test_async_reliable_outbound_status(self):
        # the response is just an acknowledgement from spine...
        outbound_response, _, _ = integration_tests.helpers.methods.get_interaction_from_template('async reliable',
                                                                        'REPC_IN150016UK05',
                                                                        '9689177621',
                                                                        'Asynchronous Reliable test')
        # we need to 'accept' the message in the queue, so it is removed and doesn't impact on subsequent tests
        integration_tests.helpers.message_retriever.get_inbound_response()
        self.assertTrue(integration_tests.helpers.methods.check_status_code(outbound_response, 202),
                        "Async Reliable outbound test failed")

    @skip('DO NOT CHECK-IN!!!!!!')
    def test_async_reliable_inbound_message_id(self):
        # send the message
        outbound_response, sent_message_id, _ = integration_tests.helpers.methods.get_interaction_from_template('async reliable',
                                                                                      'REPC_IN150016UK05',
                                                                                      '9689177699',
                                                                                      'Asynchronous Reliable test',
                                                                                                                pass_message_id=True,
                                                                                                                pass_correlation_id=False)
        # then retrieve the message Id for the response (from the queue)...
        received_message_id, _, _ = integration_tests.helpers.message_retriever.get_inbound_response()
        self.assertEqual(received_message_id, sent_message_id,
                         "Async Reliable inbound message Id test failed")

    @skip('DO NOT CHECK-IN!!!!!!')
    def test_async_reliable_inbound_correlation_id(self):
        # send the message
        outbound_response, _, sent_correlation_id = integration_tests.helpers.methods.get_interaction_from_template('async reliable',
                                                                                          'REPC_IN150016UK05',
                                                                                          '9689177710',
                                                                                          'Asynchronous Reliable test',
                                                                                                                    pass_message_id=False,
                                                                                                                    pass_correlation_id=True)
        # then retrieve the correlation Id for the response (from the queue)...
        _, received_correlation_id, _ = integration_tests.helpers.message_retriever.get_inbound_response()
        self.assertEqual(received_correlation_id, sent_correlation_id,
                         "Async Reliable inbound correlation Id test failed")

    @skip('DO NOT CHECK-IN!!!!!!')
    def test_async_reliable_inbound_response(self):
        # send the message
        integration_tests.helpers.methods.get_interaction_from_template('async reliable',
                                              'REPC_IN150016UK05',
                                              '9689177869',
                                              'Asynchronous Reliable test')
        # then retrieve the response from the queue...
        _, _, inbound_response = integration_tests.helpers.message_retriever.get_inbound_response()
        self.assertTrue(integration_tests.helpers.methods.check_response(inbound_response, 'queryResponseCode'),
                        "Async Reliable inbound response test failed")

    @skip('DO NOT CHECK-IN!!!!!!')
    def test_async_reliable_inbound_patient(self):
        # send the message
        integration_tests.helpers.methods.get_interaction_from_template('async reliable',
                                              'REPC_IN150016UK05',
                                              '9689177923',
                                              'Asynchronous Reliable test')
        # then retrieve the response from the queue...
        _, _, inbound_response = integration_tests.helpers.message_retriever.get_inbound_response()
        patient_number = integration_tests.helpers.methods.get_section(inbound_response, 'extension', 'id', 'patient')
        self.assertEqual(patient_number, '9689177923',
                         "Async Reliable inbound response test failed")
