import requests

from integration_tests.helpers import methods
from integration_tests.helpers.build_message import build_message


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
    headers['ods-code'] = 'X26'

    return requests.post(methods.get_mhs_hostname(), headers=headers, data=hl7payload)


def call_scr_adaptor(json_string):
    """ Call the SCR adaptor with the provided json string

    :param json_string: the json to be sent
    :return: the response from the adaptor
    """

    # TODO RT-186
    # once we know the scr_adaptor end point, we need to send the json_string to the scr_adaptor
    # scr_adaptor_response = requests.post(methods.get_scr_adaptor_hostname() + json_string)
    # return scr_adaptor_response.text

    # meanwhile, build an example response...
    scr_adaptor_response, message_id = build_message('REPC_IN150016UK05',
                                                     methods.get_asid(),
                                                     '9689177869',
                                                     'json message test')
    return scr_adaptor_response
