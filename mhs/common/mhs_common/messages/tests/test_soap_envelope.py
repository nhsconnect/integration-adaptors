from unittest import TestCase
from unittest.mock import patch
from pathlib import Path

from builder import pystache_message_builder
from definitions import ROOT_DIR
from mhs_common.messages import soap_envelope
from utilities import file_utilities
from utilities import message_utilities

EXPECTED_SOAP = "soap_request.xml"

SOAP_HEADERS = {'name': 'value'}
EXPECTED_MESSAGE = '<QUPA_IN040000UK32 xmlns="urn:hl7-org:v3" xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/" ' \
                   'xmlns:wsa="http://schemas.xmlsoap.org/ws/2004/08/addressing" xmlns:hl7="urn:hl7-org:v3">text</QUPA_IN040000UK32>'

MOCK_UUID = "79F49A34-9798-404C-AEC4-FD38DD81C138"
MOCK_TIMESTAMP = "2012-03-15T06:51:08Z"

EXPECTED_VALUES = {
    soap_envelope.FROM_ASID: "918999199111",
    soap_envelope.TO_ASID: "000009199092",
    soap_envelope.MESSAGE_ID: "uuid:79F49A34-9798-404C-AEC4-FD38DD81C138",
    soap_envelope.ACTION: "urn:nhs:names:services:pdsquery/QUPA_IN040000UK32",
    soap_envelope.SERVICE: "https://pds-sync.national.ncrs.nhs.uk/syncservice-pds/pds"
}

EXPECTED_MESSAGE_DIR = "mhs_common/messages/tests/expected_messages"
TEST_MESSAGE_DIR = "mhs_common/messages/tests/test_messages"

EXPECTED_HTTP_HEADERS = {
    'charset': 'UTF-8',
    'SOAPAction': 'urn:nhs:names:services:pdsquery/QUPA_IN040000UK32',
    'Content-Type': 'text/xml',
    'type': 'text/xml'
}

def get_test_message_dictionary():
    return {
        soap_envelope.FROM_ASID: "918999199111",
        soap_envelope.TO_ASID: "000009199092",
        soap_envelope.MESSAGE_ID: "79F49A34-9798-404C-AEC4-FD38DD81C138",
        soap_envelope.SERVICE: "https://pds-sync.national.ncrs.nhs.uk/syncservice-pds/pds",
        soap_envelope.ACTION: "urn:nhs:names:services:pdsquery/QUPA_IN040000UK32",
        soap_envelope.MESSAGE: EXPECTED_MESSAGE
    }


def expected_values(message=None):
    values = EXPECTED_VALUES.copy()

    if message:
        values[soap_envelope.MESSAGE] = message

    return values


class TestSoapRequestEnvelope(TestCase):

    def setUp(self):
        self.expected_message_dir = Path(ROOT_DIR) / EXPECTED_MESSAGE_DIR
        self.test_message_dir = Path(ROOT_DIR) / TEST_MESSAGE_DIR

        expected_message = file_utilities.get_file_string(str(self.expected_message_dir / EXPECTED_SOAP))
        # Pystache does not convert line endings to LF in the same way as Python does when loading the example from
        # file, so normalize the line endings of the strings being compared
        self.normalized_expected_serialized_message = file_utilities.normalize_line_endings(
            expected_message)

    @patch.object(message_utilities, "get_timestamp")
    @patch.object(message_utilities, "get_uuid")
    def test_serialize(self, mock_get_uuid, mock_get_timestamp):
        mock_get_uuid.return_value = MOCK_UUID
        mock_get_timestamp.return_value = MOCK_TIMESTAMP

        envelope = soap_envelope.SoapEnvelope(get_test_message_dictionary())

        message_id, http_headers, message = envelope.serialize()

        normalized_message = file_utilities.normalize_line_endings(message)

        self.assertEqual(MOCK_UUID, message_id)
        self.assertEqual(EXPECTED_HTTP_HEADERS, http_headers)
        self.assertEqual(self.normalized_expected_serialized_message, normalized_message)

    @patch.object(message_utilities, "get_timestamp")
    @patch.object(message_utilities, "get_uuid")
    def test_serialize_message_id_not_generated(self, mock_get_uuid, mock_get_timestamp):
        mock_get_timestamp.return_value = MOCK_TIMESTAMP

        message_dictionary = get_test_message_dictionary()
        message_dictionary[soap_envelope.MESSAGE_ID] = MOCK_UUID
        envelope = soap_envelope.SoapEnvelope(message_dictionary)

        message_id, http_headers, message = envelope.serialize()

        normalized_message = file_utilities.normalize_line_endings(message)

        mock_get_uuid.assert_not_called()
        self.assertEqual(MOCK_UUID, message_id)
        self.assertEqual(EXPECTED_HTTP_HEADERS, http_headers)
        self.assertEqual(self.normalized_expected_serialized_message, normalized_message)

    def test_serialize_required_tags(self):
        for required_tag in get_test_message_dictionary().keys():
            with self.subTest(required_tag=required_tag):
                if required_tag != soap_envelope.MESSAGE_ID:
                    test_message_dict = get_test_message_dictionary()
                    del test_message_dict[required_tag]
                    envelope = soap_envelope.SoapEnvelope(test_message_dict)

                    with self.assertRaisesRegex(pystache_message_builder.MessageGenerationError, 'Failed to find key'):
                        envelope.serialize()

    def test_from_string(self):
        with self.subTest("A valid request containing a payload"):
            message = file_utilities.get_file_string(str(self.expected_message_dir / EXPECTED_SOAP))
            expected_values_with_payload = expected_values(message=EXPECTED_MESSAGE)

            parsed_message = soap_envelope.SoapEnvelope.from_string(SOAP_HEADERS, message)

            self.assertEqual(expected_values_with_payload, parsed_message.message_dictionary)

        with self.subTest("A soap message with missing message id"):
            message = file_utilities.get_file_string(
                str(self.test_message_dir / "soap_request_with_defect.msg"))

            with self.assertRaisesRegex(
                    soap_envelope.SoapParsingError, "Weren't able to find required element message_id "
                                                    "during parsing of SOAP message"):
                soap_envelope.SoapEnvelope.from_string(SOAP_HEADERS, message)

