import os
import unittest
from pathlib import Path

from utilities.file_utilities import FileUtilities

from mhs_common.errors.ebxml_handler import handle_ebxml_error


class TestOutboundSOAPHandler(unittest.TestCase):
    message_dir = Path(os.path.dirname(os.path.abspath(__file__))) / 'test_messages'

    def test_non_200(self):
        self.assertEqual(handle_ebxml_error(202, {'Content-Type': 'text/xml'}, 'Some body'), (202, 'Some body'))

    def test_non_ebxml_fault(self):
        self.assertEqual(handle_ebxml_error(200, {'Content-Type': 'text/xml'}, '<a><b></b></a>'),
                         (200, '<a><b></b></a>'))

    def test_invalid_xml(self):
        with self.assertRaises(Exception):
            handle_ebxml_error(200, {'Content-Type': 'text/xml'}, '<a><b><b></a>')

    def test_single_error(self):
        message = FileUtilities.get_file_string(Path(self.message_dir) / 'ebxml_response_error_single.xml' )
        self.assertTrue('501319:Unknown eb:CPAId' in handle_ebxml_error(200, {'Content-Type': 'text/xml'}, message)[1])

    def test_multiple_errors(self):
        message = FileUtilities.get_file_string(Path(self.message_dir) / 'ebxml_response_error_multiple.xml')
        response = handle_ebxml_error(200, {'Content-Type': 'text/xml'}, message)[1]

        self.assertTrue('501319:Unknown eb:CPAId' in response)
        self.assertTrue('501320:Unknown something else' in response)

    def test_no_content_type(self):
        with self.assertRaises(ValueError):
            handle_ebxml_error(200, {}, 'Some body')

    def test_non_xml_content_type(self):
        with self.assertRaises(ValueError):
            self.assertRaises(AssertionError, handle_ebxml_error(200, {'Content-Type': 'text/html'}, 'Some body'))
