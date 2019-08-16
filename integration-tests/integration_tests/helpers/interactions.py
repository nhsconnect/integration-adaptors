
from integration_tests.helpers.build_scr import build_message
from integration_tests.helpers.callmhs import call_mhs


def process_request(interaction_name, template, asid, nhs_number, human_readable, pass_message_id):
    """
    Renders the template and passes it the the MHS
    :param interaction_name: the type of message
    :param template: the template to use
    :param asid: the asid, as supplied from NHS digital
    :param nhs_number: the NHS number for the test patient
    :param human_readable: the text to be sent on to SPINE
    :param pass_message_id: flag to indicate if we need to pass on the message ID
    :return: response received from the MHS
    """

    # This will be expanded to accommodate other interactions...
    if interaction_name.lower() == 'gp_summary_upload':
        scr, message_id = build_message(template, asid, nhs_number, human_readable)
        if not pass_message_id:
            message_id = None

        return process_message(interaction_name, scr, message_id)
    else:
        return 'Unknown MHS Adaptor Command'


def process_message(interaction_name, message, message_id=None):
    """
    Sends the message to the the MHS
    :param interaction_name: the type of message
    :param message: the HL7 formatted mesaage to be sent to the MHS
    :param pass_message_id: flag to indicate if we need to pass on the message ID
    :return: response received from the MHS
    """
    if message_id is None:
        return call_mhs(interaction_name, message)
    else:
        return call_mhs(interaction_name, message, message_id=message_id)
