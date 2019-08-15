import requests

from integration_tests.helpers import methods
from integration_tests.helpers.build_message import build_message


def process_request(interaction_name, asid, nhs_number, human_readable, pass_message_id):
    """ Renders the template and passes it the the MHS

    :param interaction_name: the type of message (also the template name)
    :param asid: the asid, as supplied from NHS digital
    :param nhs_number: the NHS number for the test patient
    :param human_readable: the text to be sent on to SPINE
    :param pass_message_id: flag to indicate if we need to pass on the message ID
    :return: response received from the MHS
    """
    scr, message_id = build_message(asid, nhs_number, human_readable)
    if not pass_message_id:
        message_id = None

    return call_mhs(interaction_name, scr, message_id)


def call_mhs(mhs_command, hl7payload, message_id=None):
    """Call the MHS with the provided details.

    :param mhs_command: The command/interaction name to call the MHS with.
    :param hl7payload: The HL7 payload to send to the MHS.
    :param message_id: The message id to optionally pass as a query param
    :return: The response returned by the MHS.
    """
    headers = {'Interaction-Id': mhs_command}
    if message_id is not None:
        headers['Message-Id'] = message_id

    response = requests.post(methods.get_mhs_hostname(), headers=headers, data=hl7payload)
    return response.text


def call_scr_adaptor(json_string):
    """ Call the SCR adaptor with the provided json string

    :param json_string: the json to be sent
    :return: the response from the adaptor
    """

    # TODO
    # once we know the scr_adaptor end point, we need to send the json_string to the scr_adaptor
    # scr_adaptor_response = requests.post(methods.get_scr_adaptor_hostname() + json_string)
    # return scr_adaptor_response.text

    # meanwhile, build an example response...
    scr_adaptor_response, message_id = build_message('REPC_IN150016UK05',
                                                     methods.get_asid(),
                                                     '9689177869',
                                                     'json message test')
    return scr_adaptor_response
