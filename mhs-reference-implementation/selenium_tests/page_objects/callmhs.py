import requests

from selenium_tests.page_objects import methods


def call_mhs(mhs_command, hl7payload):
    """Call the MHS with the provided details.

    :param mhs_command: The command/interaction name to call the MHS with.
    :param hl7payload: The HL7 payload to send to the MHS.
    :return: The response returned by the MHS.
    """

    response = requests.post(methods.get_hostname() + mhs_command, data=hl7payload)
    return response.text
