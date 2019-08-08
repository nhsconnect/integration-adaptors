import requests

from selenium_tests.page_objects import methods


def call_mhs(mhs_command, hl7payload, message_id=None):
    """Call the MHS with the provided details.

    :param mhs_command: The command/interaction name to call the MHS with.
    :param hl7payload: The HL7 payload to send to the MHS.
    :param message_id: The message id to optionally pass as a query param
    :return: The response returned by the MHS.
    """

    params = {} if message_id is None else {'messageId': message_id}
    headers = {'Interaction-Id': mhs_command}
    response = requests.post(methods.get_hostname(), params=params, headers=headers, data=hl7payload)
    return response.text
