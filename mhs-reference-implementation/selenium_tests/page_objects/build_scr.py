import datetime

from utilities import message_utilities
from selenium_tests.page_objects import message_builder

TIMESTAMP_FORMAT = "%Y%m%d%H%M%S"
MESSAGE_XML = "xml_IN150016UK05"

UUID = 'uuid'
TIMESTAMP = 'timestamp'
ASID = 'asid'
PATIENT_NHS_NUMBER = 'patient_nhs_number'
PAYLOAD = 'payload'


def build_scr(asid, patient_nhs_number, payload):
    """Build a GP summary upload message

    :param asid: The ASID of this node.
    :param patient_nhs_number: The NHS number of the patient this record belongs to.
    :param payload: The human readable payload to be included in the summary message.
    :return: The GP summary message.
    """

    current_utc_time = datetime.datetime.utcnow()
    timestamp = current_utc_time.strftime(TIMESTAMP_FORMAT)
    uuid = message_utilities.MessageUtilities.get_uuid()

    xml_message = message_builder.MustacheMessageBuilder(MESSAGE_XML).build_message({
        UUID: uuid,
        TIMESTAMP: timestamp,
        ASID: asid,
        PAYLOAD: payload,
        PATIENT_NHS_NUMBER: patient_nhs_number
    })

    return xml_message
