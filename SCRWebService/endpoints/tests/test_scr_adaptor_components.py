import json
import pathlib

from builder.pystache_message_builder import MessageGenerationError
from scr import gp_summary_upload
from utilities import file_utilities, test_utilities
from definitions import ROOT_DIR
from tornado.testing import AsyncHTTPTestCase
from tornado.web import Application
from unittest import mock
from endpoints import summary_care_record
from message_handling import message_sender, message_forwarder

GP_SUMMARY_UPLOAD_URL = "/"

complete_data_path = pathlib.Path(ROOT_DIR) / 'endpoints' / 'tests' / 'data' / 'complete_input.json'


class TestSummaryCareRecord(AsyncHTTPTestCase):
    """Tests associated with the Summary Care Record endpoint"""

    def get_app(self):
        interactions = {
            'SCR_GP_SUMMARY_UPLOAD': gp_summary_upload.GpSummaryUpload()
        }
        address = 'http://Fixed-Address.com'
        sender = message_sender.MessageSender(address)
        forwarder = message_forwarder.MessageForwarder(interactions, sender)

        return Application([(r"/", summary_care_record.SummaryCareRecord, dict(forwarder=forwarder))])

    @mock.patch('comms.common_https.CommonHttps.make_request')
    def test_scr_adaptor_calls_mhs_end_point(self, request_mock):
        body = file_utilities.FileUtilities.get_file_dict(complete_data_path)
        request_mock.return_value = test_utilities.awaitable("Response message")

        response = self.fetch(GP_SUMMARY_UPLOAD_URL, method='POST', headers={'interaction-id': 'SCR_GP_SUMMARY_UPLOAD'},
                              body=json.dumps(body))

        self.assertEqual(response.body.decode(), "Response message")

    @mock.patch('comms.common_https.CommonHttps.make_request')
    def test_exception_raised_during_message_sending_raises_MessageSendingError(self, request_mock):
        body = file_utilities.FileUtilities.get_file_dict(complete_data_path)
        request_mock.side_effect = Exception('Failed to route the dam packet')

        response = self.fetch(GP_SUMMARY_UPLOAD_URL, method='POST', headers={'interaction-id': 'SCR_GP_SUMMARY_UPLOAD'},
                              body=json.dumps(body))

        self.assertEqual(response.code, 500)
        self.assertIn('Failed to route the dam packet', response.body.decode())