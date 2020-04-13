import os
from pathlib import Path
from xml.etree import ElementTree
from unittest import TestCase

import utilities.file_utilities as file_utilities

from mhs_common.messages.soap_fault_envelope import SOAPFault


class TestSOAPFault(TestCase):
    message_dir = Path(os.path.dirname(os.path.abspath(__file__))) / 'test_messages'

    def test_is_soap_empty(self):
        message = file_utilities.get_file_string(Path(self.message_dir) / 'soapfault_response_empty.xml' )
        self.assertTrue(SOAPFault.is_soap_fault(ElementTree.fromstring(message)))

    def test_is_soap_negative(self):
        message = file_utilities.get_file_string(Path(self.message_dir) / 'ebxml_header.xml')
        self.assertFalse(SOAPFault.is_soap_fault(ElementTree.fromstring(message)))

    def test_soap_fault_single(self):
        message = file_utilities.get_file_string(Path(self.message_dir) / 'soapfault_response_single_error.xml')
        self.assertTrue(SOAPFault.is_soap_fault(ElementTree.fromstring(message)))

    def test_soap_fault_multiple(self):
        message = file_utilities.get_file_string(Path(self.message_dir) / 'soapfault_response_multiple_errors.xml')
        self.assertTrue(SOAPFault.is_soap_fault(ElementTree.fromstring(message)))

    def test_soap_fault_empty(self):
        self.assertFalse(SOAPFault.is_soap_fault(None))

    def test_from_string_single(self):
        message = file_utilities.get_file_string(Path(self.message_dir) / 'soapfault_response_single_error.xml')
        fault: SOAPFault = SOAPFault.from_string({}, message)
        self.assertEqual(fault.fault_code, 'SOAP:Server')
        self.assertEqual(fault.fault_string, 'Application Exception')
        self.assertEqual(len(fault.error_list), 1)

        self.assertEqual(fault.error_list[0]['codeContext'], 'urn:nhs:names:error:tms')
        self.assertEqual(fault.error_list[0]['errorCode'], '200')
        self.assertEqual(fault.error_list[0]['severity'], 'Error')
        self.assertEqual(fault.error_list[0]['location'], 'Not Supported')
        self.assertEqual(fault.error_list[0]['description'], 'System failure to process message - default')

    def test_from_string_multiple(self):
        message = file_utilities.get_file_string(Path(self.message_dir) / 'soapfault_response_multiple_errors.xml')
        fault: SOAPFault = SOAPFault.from_string({}, message)
        self.assertEqual(fault.fault_code, 'SOAP:Server')
        self.assertEqual(fault.fault_string, 'Application Exception')
        self.assertEqual(len(fault.error_list), 2)

        self.assertEqual(fault.error_list[0]['codeContext'], 'urn:nhs:names:error:tms')
        self.assertEqual(fault.error_list[0]['errorCode'], '200')
        self.assertEqual(fault.error_list[0]['severity'], 'Error')
        self.assertEqual(fault.error_list[0]['location'], 'Not Supported')
        self.assertEqual(fault.error_list[0]['description'], 'System failure to process message - default')

        self.assertEqual(fault.error_list[1]['codeContext'], 'urn:nhs:names:error:tms')
        self.assertEqual(fault.error_list[1]['errorCode'], '201')
        self.assertEqual(fault.error_list[1]['severity'], 'Error')
        self.assertEqual(fault.error_list[1]['location'], 'Not Supported')
        self.assertEqual(fault.error_list[1]['description'], 'The message is not well formed')

    def test_soap_error_codes_are_retriable_or_not(self):
        errors_and_expected = [("a retriable failure to process message error code 200", [200], True),
                               ("a retriable routing failure error code 206", [206], True),
                               ("a retriable failure storing memo error code 208", [208], True),
                               ("a NON retriable error code 300", [300], False),
                               ("a NON retriable set of error codes 300, 207", [300, 207], False),
                               ("a mix of retriable and NON retriable error codes 300, 206", [300, 206], False),
                               ("a mix of retriable and NON retriable error codes 206, 300", [206, 300], False),
                               ("a set of retriable error codes 208, 206", [208, 206], True)
                               ]
        for description, error, expected_result in errors_and_expected:
            with self.subTest(description):
                result = SOAPFault.is_soap_fault_retriable(error)

                self.assertEqual(result, expected_result)
