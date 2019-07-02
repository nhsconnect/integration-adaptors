from unittest import TestSuite, TextTestRunner

from mhs.builder.tests import test_ebxml_ack_message_builder, test_ebxml_request_message_builder
from mhs.config.tests import test_interactions
from mhs.handler.tests import test_async_response_handler, test_client_request_handler
from mhs.parser.tests import test_ebxml_message_parser
from mhs.sender.tests import test_sender
from mhs.transport.tests import test_http_transport


def test_suite():
    suite = TestSuite()

    suite.addTest(test_ebxml_ack_message_builder.TestEbXmlAckMessageBuilder('test_build_message'))
    suite.addTest(test_ebxml_request_message_builder.TestEbXmlRequestMessageBuilder('test_build_message'))

    suite.addTest(test_interactions.TestInteractionsConfigFile('test_get_interaction_details'))

    suite.addTest(test_async_response_handler.TestAsyncResponseHandler('test_post'))
    suite.addTest(test_async_response_handler.TestAsyncResponseHandler('test_post_no_callback'))
    suite.addTest(test_client_request_handler.TestClientRequestHandler('test_post_synchronous_message'))
    suite.addTest(test_client_request_handler.TestClientRequestHandler('test_post_with_invalid_interaction_name'))
    suite.addTest(test_client_request_handler.TestClientRequestHandler('test_post_asynchronous_message_times_out'))

    suite.addTest(test_ebxml_message_parser.TestEbXmlMessageParser('test_parse_message'))
    suite.addTest(test_ebxml_message_parser.TestEbXmlMessageParser('test_parse_message_with_no_values'))
    suite.addTest(test_ebxml_message_parser.TestEbXmlRequestMessageParser('test_parse_message'))

    suite.addTest(test_sender.TestSender('test_prepare_message_async'))
    suite.addTest(test_sender.TestSender('test_prepare_message_sync'))
    suite.addTest(test_sender.TestSender('test_build_message_incorrect_interaction_name'))
    suite.addTest(test_sender.TestSender('test_sender'))
    suite.addTest(test_sender.TestSender('test_send_message_incorrect_interaction_name'))

    suite.addTest(test_http_transport.TestHttpTransport('test_make_request'))
    suite.addTest(test_http_transport.TestHttpTransport('test_build_headers'))
    suite.addTest(test_http_transport.TestHttpTransport('test_get_request_method'))

    return suite


if __name__ == '__main__':
    runner = TextTestRunner()
    runner.run(test_suite())
