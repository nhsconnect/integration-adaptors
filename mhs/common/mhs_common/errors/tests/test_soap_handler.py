import json
import os
import unittest
from pathlib import Path

import utilities.file_utilities as file_utilities

from mhs_common.errors.soap_handler import handle_soap_error


class TestOutboundSOAPHandler(unittest.TestCase):
    message_dir = Path(os.path.dirname(os.path.abspath(__file__))) / 'test_messages'

    def test_non_500(self):
        self.assertEqual(handle_soap_error(202, {'Content-Type': 'text/html'}, 'Some body'), (202, 'Some body', []))

    def test_non_soap_fault(self):
        with self.assertRaises(AssertionError):
            handle_soap_error(500, {'Content-Type': 'text/xml'}, '<a><b></b></a>')

    def test_invalid_xml(self):
        with self.assertRaises(Exception):
            handle_soap_error(500, {'Content-Type': 'text/xml'}, '<a><b><b></a>')

    def test_single_error(self):
        message = file_utilities.get_file_string(Path(self.message_dir) / 'soapfault_response_single_error.xml')
        resp_json = json.loads(handle_soap_error(500, {'Content-Type': 'text/xml'}, message)[1])

        self.assert_json_error_root(resp_json)
        self.assert_json_with_first_error(resp_json)

    def test_multiple_errors(self):
        message = file_utilities.get_file_string(Path(self.message_dir) / 'soapfault_response_multiple_errors.xml')
        resp_json = json.loads(handle_soap_error(500, {'Content-Type': 'text/xml'}, message)[1])

        self.assert_json_error_root(resp_json)
        self.assert_json_with_first_error(resp_json)
        self.assert_json_with_second_error(resp_json)

    def test_no_content_type(self):
        with self.assertRaises(ValueError):
            handle_soap_error(500, {}, 'Some body')

    def test_non_xml_content_type(self):
        with self.assertRaises(ValueError):
            handle_soap_error(500, {'Content-Type': 'text/html'}, 'Some body')

    def assert_json_error_root(self, resp_json):
        self.assertEqual(resp_json['error_message'], "Error(s) received from Spine. Contact system administrator.")
        self.assertEqual(resp_json['process_key'], "SOAP_ERROR_HANDLER0002")

    def assert_json_with_first_error(self, resp_json):
        self.assertEqual(resp_json['errors'][0]['codeContext'], "urn:nhs:names:error:tms")
        self.assertEqual(resp_json['errors'][0]['description'], "System failure to process message - default")
        self.assertEqual(resp_json['errors'][0]['errorCode'], "200")
        self.assertEqual(resp_json['errors'][0]['errorType'], "soap_fault")
        self.assertEqual(resp_json['errors'][0]['severity'], "Error")

    def assert_json_with_second_error(self, resp_json):
        self.assertEqual(resp_json['errors'][1]['codeContext'], "urn:nhs:names:error:tms")
        self.assertEqual(resp_json['errors'][1]['description'], "The message is not well formed")
        self.assertEqual(resp_json['errors'][1]['errorCode'], "201")
        self.assertEqual(resp_json['errors'][1]['errorType'], "soap_fault")
        self.assertEqual(resp_json['errors'][1]['severity'], "Error")
