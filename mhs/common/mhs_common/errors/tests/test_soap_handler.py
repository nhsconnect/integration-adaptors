import os
import unittest
from pathlib import Path

from utilities.file_utilities import FileUtilities

from mhs_common.errors.soap_handler import handle_soap_error


class TestOutboundSOAPHandler(unittest.TestCase):
    message_dir = Path(os.path.dirname(os.path.abspath(__file__))) / 'test_messages'

    def test_non_500(self):
        self.assertEqual(handle_soap_error(202, {'Content-Type': 'text/html'}, 'Some body'), (202, 'Some body'))

    def test_non_soap_fault(self):
        with self.assertRaises(AssertionError):
            handle_soap_error(500, {'Content-Type': 'text/xml'}, '<a><b></b></a>')

    def test_invalid_xml(self):
        with self.assertRaises(Exception):
            handle_soap_error(500, {'Content-Type': 'text/xml'}, '<a><b><b></a>')

    def test_single_error(self):
        message = FileUtilities.get_file_string(Path(self.message_dir) / 'soapfault_response_single_error.xml' )
        self.assertTrue('System failure to process message - default' in
                        handle_soap_error(500, {'Content-Type': 'text/xml'}, message)[1])

    def test_multiple_errors(self):
        message = FileUtilities.get_file_string(Path(self.message_dir) / 'soapfault_response_multiple_errors.xml')
        response = handle_soap_error(500, {'Content-Type': 'text/xml'}, message)[1]

        self.assertTrue('System failure to process message - default' in response)
        self.assertTrue('The message is not well formed' in response)

    def test_no_content_type(self):
        with self.assertRaises(ValueError):
            handle_soap_error(500, {}, 'Some body')

    def test_non_xml_content_type(self):
        with self.assertRaises(ValueError):
            handle_soap_error(500, {'Content-Type': 'text/html'}, 'Some body')
