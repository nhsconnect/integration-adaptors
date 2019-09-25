import requests

from utilities import message_utilities

from integration_tests.helpers import methods
from integration_tests.helpers.build_message import build_message


def process_request(template, asid, nhs_number, human_readable, pass_message_id, pass_correlation_id, sync_async):
    """ Renders the template and passes it the the MHS

    :param template: the template name
    :param asid: the asid, as supplied from NHS digital
    :param nhs_number: the NHS number for the test patient
    :param human_readable: the text to be sent on to SPINE
    :param pass_message_id: flag to indicate if we need to pass on the message ID
    :param pass_correlation_id: flag to indicate if we need to pass on the correlation ID
    :param sync_async: What the sync-async header flag should be set to
    :return: A tuple of the response received from the MHS, the message ID and the correlation ID
    """
    scr, message_id = build_message(template, asid, nhs_number, human_readable)
    correlation_id = message_utilities.MessageUtilities.get_uuid()
    response = call_mhs(template, scr, message_id, pass_message_id, correlation_id, pass_correlation_id, sync_async,
                        asid)

    return response, message_id, correlation_id


def call_mhs(mhs_command, hl7payload, message_id, pass_message_id, correlation_id, pass_correlation_id, sync_async,
             from_asid):
    """Call the MHS with the provided details.

    :param mhs_command: The command/interaction name to call the MHS with.
    :param hl7payload: The HL7 payload to send to the MHS.
    :param message_id: The message ID to (optionally) pass as a query param
    :param pass_message_id: flag to indicate if we need to pass on the message ID
    :param correlation_id: The correlation ID to (optionally) pass as a query param
    :param pass_correlation_id: flag to indicate if we need to pass on the correlation ID
    :return: The response returned by the MHS.
    """
    headers = {'Interaction-Id': mhs_command}
    if pass_message_id:
        headers['Message-Id'] = message_id

    if pass_correlation_id:
        headers['Correlation-Id'] = correlation_id

    headers['sync-async'] = 'true' if sync_async else 'false'
    headers['from-asid'] = f'{from_asid}'

    return requests.post(methods.get_mhs_hostname(), headers=headers, data=hl7payload)

