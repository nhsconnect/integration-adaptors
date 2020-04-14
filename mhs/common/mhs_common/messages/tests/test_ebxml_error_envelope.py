import os
from pathlib import Path
from xml.etree import ElementTree
from unittest import TestCase

import utilities.file_utilities as file_utilities

from mhs_common.messages.ebxml_error_envelope import EbxmlErrorEnvelope


class TestEbxmlEnvelope(TestCase):
    message_dir = Path(os.path.dirname(os.path.abspath(__file__))) / 'test_messages'

    def test_is_ebxml_empty(self):
        message = file_utilities.get_file_string(self.message_dir / 'ebxml_response_error_empty.xml' )
        self.assertTrue(EbxmlErrorEnvelope.is_ebxml_error(ElementTree.fromstring(message)))

    def test_is_ebxml_negative(self):
        message = file_utilities.get_file_string(self.message_dir / 'ebxml_header.xml')
        self.assertFalse(EbxmlErrorEnvelope.is_ebxml_error(ElementTree.fromstring(message)))

    def test_ebxml_error_single(self):
        message = file_utilities.get_file_string(self.message_dir / 'ebxml_response_error_single.xml')
        self.assertTrue(EbxmlErrorEnvelope.is_ebxml_error(ElementTree.fromstring(message)))

    def test_ebxml_error_multiple(self):
        message = file_utilities.get_file_string(self.message_dir / 'ebxml_response_error_multiple.xml')
        self.assertTrue(EbxmlErrorEnvelope.is_ebxml_error(ElementTree.fromstring(message)))

    def test_ebxml_error_empty(self):
        self.assertFalse(EbxmlErrorEnvelope.is_ebxml_error(None))

    def test_from_string_single(self):
        message = file_utilities.get_file_string(self.message_dir / 'ebxml_response_error_single.xml')
        ebxml_error: EbxmlErrorEnvelope = EbxmlErrorEnvelope.from_string(message)
        self.assertEqual(len(ebxml_error.errors), 1)

        self.assertEqual(ebxml_error.errors[0]['codeContext'], 'urn:oasis:names:tc:ebxml-msg:service:errors')
        self.assertEqual(ebxml_error.errors[0]['errorCode'], 'ValueNotRecognized')
        self.assertEqual(ebxml_error.errors[0]['severity'], 'Error')
        self.assertEqual(ebxml_error.errors[0]['Description'], '501319:Unknown eb:CPAId')

    def test_from_string_multiple(self):
        message = file_utilities.get_file_string(self.message_dir / 'ebxml_response_error_multiple.xml')
        ebxml_error: EbxmlErrorEnvelope = EbxmlErrorEnvelope.from_string(message)
        self.assertEqual(len(ebxml_error.errors), 2)

        self.assertEqual(ebxml_error.errors[0]['codeContext'], 'urn:oasis:names:tc:ebxml-msg:service:errors')
        self.assertEqual(ebxml_error.errors[0]['errorCode'], 'ValueNotRecognized')
        self.assertEqual(ebxml_error.errors[0]['severity'], 'Error')
        self.assertEqual(ebxml_error.errors[0]['Description'], '501319:Unknown eb:CPAId')

        self.assertEqual(ebxml_error.errors[1]['codeContext'], 'urn:oasis:names:tc:ebxml-msg:service:errors')
        self.assertEqual(ebxml_error.errors[1]['errorCode'], 'ValueNotRecognized')
        self.assertEqual(ebxml_error.errors[1]['severity'], 'Error')
        self.assertEqual(ebxml_error.errors[1]['Description'], '501320:Unknown something else')
