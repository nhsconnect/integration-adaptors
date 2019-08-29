import datetime

from utilities import message_utilities
from integration_tests.helpers import message_builder

TIMESTAMP_FORMAT = "%Y%m%d%H%M%S"

UUID = 'uuid'
TIMESTAMP = 'timestamp'
ASID = 'asid'
PATIENT_NHS_NUMBER = 'patient_nhs_number'
PAYLOAD = 'payload'
TO_PARTY_ID = 'to_party_id'
FILE_UPLOAD = 'file_upload'
DISSENT_OVERRIDE = 'dissentOverride'
USE_DATE_FILTER = 'useDateFilter'


def build_message(template, asid, patient_nhs_number, payload):
    """Build an upload message

    :param template: The Name of the template to be used.
    :param asid: The ASID of this node.
    :param patient_nhs_number: The NHS number of the patient this record belongs to.
    :param payload: The human readable payload to be included in the summary message.
    :return: A tuple of the message and the message id (UUID) used in it.
    """
    current_utc_time = datetime.datetime.utcnow()
    timestamp = current_utc_time.strftime(TIMESTAMP_FORMAT)
    uuid = message_utilities.MessageUtilities.get_uuid()
    to_party_id = 'YES-0000806'
    file_upload = 'test file will go here'
    dissentOverride = '0'
    useDateFilter = False

    message = message_builder.MustacheMessageBuilder(template).build_message({
        UUID: uuid,
        TIMESTAMP: timestamp,
        ASID: asid,
        PAYLOAD: payload,
        PATIENT_NHS_NUMBER: patient_nhs_number,
        TO_PARTY_ID: to_party_id,
        FILE_UPLOAD: file_upload,
        DISSENT_OVERRIDE: dissentOverride,
        USE_DATE_FILTER: useDateFilter
    })

    return message, uuid
