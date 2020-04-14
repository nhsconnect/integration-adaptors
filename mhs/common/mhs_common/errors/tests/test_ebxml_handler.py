import json
import os
import unittest
from pathlib import Path

from defusedxml import ElementTree
import utilities.file_utilities as file_utilities

from mhs_common.errors.ebxml_handler import handle_ebxml_error


class TestEbxmlHandler(unittest.TestCase):
    message_dir = Path(os.path.dirname(os.path.abspath(__file__))) / 'test_messages'

    def test_non_200(self):
        self.assertEqual(handle_ebxml_error(202, {'Content-Type': 'text/xml'}, ''), (202, ''))

    def test_non_ebxml_fault(self):
        self.assertEqual(handle_ebxml_error(200, {'Content-Type': 'text/xml'}, '<a><b></b></a>'),
                         (200, '<a><b></b></a>'))

    def test_invalid_xml(self):
        with self.assertRaises(ElementTree.ParseError):
            handle_ebxml_error(200, {'Content-Type': 'text/xml'}, '<a><b><b></a>')

    def test_single_error(self):
        message = file_utilities.get_file_string(self.message_dir / 'ebxml_response_error_single.xml')
        resp_json = json.loads(handle_ebxml_error(200, {'Content-Type': 'text/xml'}, message)[1])

        self.assert_json_error_root(resp_json)
        self.assert_json_with_first_error(resp_json)

    def test_multiple_errors(self):
        message = file_utilities.get_file_string(self.message_dir / 'ebxml_response_error_multiple.xml')
        resp_json = json.loads(handle_ebxml_error(200, {'Content-Type': 'text/xml'}, message)[1])

        self.assert_json_error_root(resp_json)
        self.assert_json_with_first_error(resp_json)
        self.assert_json_with_second_error(resp_json)

    def test_no_content_type(self):
        with self.assertRaises(ValueError):
            handle_ebxml_error(200, {}, 'Some body')

    def test_non_xml_content_type(self):
        with self.assertRaises(ValueError):
            handle_ebxml_error(200, {'Content-Type': 'text/html'}, 'Some body')

    def test_empty_body(self):
        code, body = handle_ebxml_error(200, {'Content-Type': 'text/xml'}, '')

        self.assertEqual(code, 200)
        self.assertEqual(body, '')

    def assert_json_error_root(self, resp_json):
        self.assertEqual(resp_json['error_message'], "Error(s) received from Spine. Contact system administrator.")
        self.assertEqual(resp_json['process_key'], "EBXML_ERROR_HANDLER0005")

    def assert_json_with_first_error(self, resp_json):
        self.assertEqual(resp_json['errors'][0]['Description'], "501319:Unknown eb:CPAId")
        self.assertEqual(resp_json['errors'][0]['codeContext'], "urn:oasis:names:tc:ebxml-msg:service:errors")
        self.assertEqual(resp_json['errors'][0]['errorCode'], "ValueNotRecognized")
        self.assertEqual(resp_json['errors'][0]['errorType'], "ebxml_error")
        self.assertEqual(resp_json['errors'][0]['severity'], "Error")

    def assert_json_with_second_error(self, resp_json):
        self.assertEqual(resp_json['errors'][1]['Description'], "501320:Unknown something else")
        self.assertEqual(resp_json['errors'][1]['codeContext'], "urn:oasis:names:tc:ebxml-msg:service:errors")
        self.assertEqual(resp_json['errors'][1]['errorCode'], "ValueNotRecognized")
        self.assertEqual(resp_json['errors'][1]['errorType'], "ebxml_error")
        self.assertEqual(resp_json['errors'][1]['severity'], "Error")
