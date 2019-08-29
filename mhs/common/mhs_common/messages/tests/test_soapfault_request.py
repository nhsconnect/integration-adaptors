import os
from xml.etree import ElementTree
from unittest import TestCase

from mhs_common.messages.soap_fault import SOAPFault, NS


class TestSOAPFaultRequest(TestCase):
    def test_is_soap_fault(self):
        with open(os.path.join('test_messages', 'soapfault_request.xml')) as f:
            message = f.read()

        self.assertTrue(SOAPFault.is_soap_fault(ElementTree.fromstring(message)))

        with open(os.path.join('test_messages', 'ebxml_header.xml')) as f:
            message = f.read()

        self.assertFalse(SOAPFault.is_soap_fault(ElementTree.fromstring(message)))
        self.assertFalse(SOAPFault.is_soap_fault(None))
