import datetime

from utilities import message_utilities
from integration_tests.helpers import message_builder
from integration_tests.helpers.asid_provider import get_asid

TIMESTAMP_FORMAT = "%Y%m%d%H%M%S"

UUID = 'uuid'
TIMESTAMP = 'timestamp'
ASID = 'asid'
PATIENT_NHS_NUMBER = 'patient_nhs_number'
TO_PARTY_ID = 'to_party_id'
FILE_UPLOAD = 'file_upload'
DISSENT_OVERRIDE = 'dissentOverride'
USE_DATE_FILTER = 'useDateFilter'
DOCUMENT_TYPE = 'documentType'
TO_ASID = 'to_asid'


def build_message(template, patient_nhs_number):
    """Build an upload message

    :param template: The Name of the template to be used.
    :param patient_nhs_number: The NHS number of the patient this record belongs to.
    :param payload: The human readable payload to be included in the summary message.
    :return: A tuple of the message and the message id (UUID) used in it.
    """
    current_utc_time = datetime.datetime.utcnow()
    timestamp = current_utc_time.strftime(TIMESTAMP_FORMAT)
    uuid = message_utilities.MessageUtilities.get_uuid()
    to_party_id = 'YES-0000806'
    file_upload = 'test file will go here'
    dissent_override = '0'
    use_date_filter = False
    document_type = '196971000000103'

    message = message_builder.MustacheMessageBuilder(template).build_message({
        UUID: uuid,
        TIMESTAMP: timestamp,
        ASID: get_asid(),
        TO_ASID: '928942012545',
        PATIENT_NHS_NUMBER: patient_nhs_number,
        TO_PARTY_ID: to_party_id,
        FILE_UPLOAD: file_upload,
        DISSENT_OVERRIDE: dissent_override,
        USE_DATE_FILTER: use_date_filter,
        DOCUMENT_TYPE: document_type
    })

    return message, uuid
