"""This module defines the envelope used to wrap synchronous messages to be sent to a remote MHS."""
import copy
import json
from pathlib import Path
from typing import Dict, Tuple, Union

import lxml.etree as ET

from comms.http_headers import HttpHeaders
from utilities import integration_adaptors_logger as log, message_utilities

from definitions import ROOT_DIR
from mhs_common.messages import envelope

SOAP_CONTENT_TYPE_VALUE = 'text/xml'

XSLT_DIR = 'mhs_common/messages/xslt'
SOAP_HEADER_XSLT = 'soap_header.xslt'
SOAP_BODY_XSLT = 'soap_body.xslt'
FROM_ASID = "from_asid"
TO_ASID = "to_asid"
SERVICE = "service"
ACTION = "action"
MESSAGE_ID = 'message_id'
TIMESTAMP = 'timestamp'
MESSAGE = 'hl7_message'

REQUIRED_SOAP_ELEMENTS = [FROM_ASID, TO_ASID, MESSAGE_ID, SERVICE, ACTION, MESSAGE]

SOAP_TEMPLATE = "soap_request"

logger = log.IntegrationAdaptorsLogger(__name__)

soap_header_transformer_path = str(Path(ROOT_DIR) / XSLT_DIR / SOAP_HEADER_XSLT)
soap_body_transformer_path = str(Path(ROOT_DIR) / XSLT_DIR / SOAP_BODY_XSLT)


class SoapEnvelope(envelope.Envelope):
    """An envelope that contains a message to be sent synchronously to a remote MHS."""

    def __init__(self, message_dictionary: Dict[str, Union[str, bool]]):
        """Create a new SoapEnvelope that populates the message with the provided dictionary.

        :param message_dictionary: The dictionary of values to use when populating the template.
        """
        super().__init__(SOAP_TEMPLATE, message_dictionary)

    def serialize(self) -> Tuple[str, Dict[str, str], str]:
        """Produce a serialised representation of this SOAP message by populating a Mustache template with this
        object's properties.

        :return: A tuple string containing the message ID, HTTP headers to be sent with the message and the message
        itself.
        """
        soap_message_dictionary = copy.deepcopy(self.message_dictionary)

        message_id = soap_message_dictionary.get(MESSAGE_ID)
        if not message_id:
            message_id = message_utilities.get_uuid()
            soap_message_dictionary[MESSAGE_ID] = message_id
        timestamp = message_utilities.get_timestamp()
        soap_message_dictionary[TIMESTAMP] = timestamp

        logger.info('Creating SOAP message with {MessageId} and {Timestamp}',
                    fparams={'MessageId': message_id, 'Timestamp': timestamp})

        message = self.message_builder.build_message(soap_message_dictionary)
        http_headers = {'charset': 'UTF-8',
                        'SOAPAction': soap_message_dictionary[ACTION],
                        HttpHeaders.CONTENT_TYPE: SOAP_CONTENT_TYPE_VALUE,
                        'type': SOAP_CONTENT_TYPE_VALUE}

        return message_id, http_headers, message

    @classmethod
    def from_string(cls, headers: Dict[str, str], message: str):
        """Parse the provided message string and create an instance of an SoapEnvelope.

        :param headers A dictionary of headers received with the message.
        :param message: The message to be parsed.
        :return: An instance of an SoapEnvelope constructed from the message.
        """
        xml_message = ET.fromstring(bytes(bytearray(message, encoding='utf-8')))
        soap_header_transformer = ET.XSLT(ET.parse(soap_header_transformer_path))
        soap_body_transformer = ET.XSLT(ET.parse(soap_body_transformer_path))

        try:
            soap_headers = str(soap_header_transformer(xml_message, **headers))
            soap_body = str(soap_body_transformer(xml_message, **headers))
        except ET.XSLTApplyError as ae:
            logger.error("An error occurred when transforming the SOAP XML message")
            raise SoapParsingError(f"An error occurred when transforming the SOAP XML message") from ae
        except Exception as e:
            logger.error("An unexpected error occurred when applying an XSLT to SOAP XML message")
            raise SoapParsingError(f"An unexpected error occurred when applying an XSLT to SOAP XML message") from e

        extracted_values = json.loads(soap_headers)
        logger.info('Extracted {extracted_values} from message', fparams={'extracted_values': extracted_values})
        extracted_values[MESSAGE] = soap_body

        for required_element in REQUIRED_SOAP_ELEMENTS:
            if not extracted_values[required_element]:
                logger.error("Weren't able to find required element {required_param} during parsing of SOAP "
                             "message.", fparams={'required_param': required_element})
                raise SoapParsingError(f"Weren't able to find required element {required_element} during parsing "
                                       f"of SOAP message")

        return SoapEnvelope(extracted_values)


class SoapParsingError(Exception):
    """Raised when an error was encountered during parsing of a SOAP message."""
    pass
