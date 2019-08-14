import datetime

from integration_tests.page_objects import message_builder
from utilities import message_utilities


TIMESTAMP_FORMAT = "%Y%m%d%H%M%S"

UUID = 'uuid'
TIMESTAMP = 'timestamp'
ASID = 'asid'
PATIENT_NHS_NUMBER = 'patient_nhs_number'
PAYLOAD = 'payload'


def build_scr_json(template, asid, patient_nhs_number, payload):
    """Build a GP summary upload json message

    :param asid: The ASID of this node.
    :param patient_nhs_number: The NHS number of the patient this record belongs to.
    :param payload: The human readable payload to be included in the summary message.
    :return: A tuple of the GP summary message and the message id (UUID) used in it.
    """

    current_utc_time = datetime.datetime.utcnow()
    timestamp = current_utc_time.strftime(TIMESTAMP_FORMAT)
    uuid = message_utilities.MessageUtilities.get_uuid()

    json_message = message_builder.MustacheMessageBuilder(template).build_message({
        UUID: uuid,
        TIMESTAMP: timestamp,
        ASID: asid,
        PAYLOAD: payload,
        PATIENT_NHS_NUMBER: patient_nhs_number
    })

    return json_message, uuid
