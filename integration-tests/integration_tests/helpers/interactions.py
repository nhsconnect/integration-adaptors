
from integration_tests.helpers.build_scr import build_message
from integration_tests.helpers.callmhs import call_mhs


def process_request(interaction_name, asid, nhs_number, human_readable, pass_message_id):
    # This will be expanded to accommodate other interactions...
    if interaction_name.lower() == 'gp_summary_upload':
        scr, message_id = build_message("xml_IN150016UK05", asid, nhs_number, human_readable)

        if pass_message_id:
            return call_mhs(interaction_name, scr, message_id=message_id)
        else:
            return call_mhs(interaction_name, scr)
    else:
        return 'Unknown MHS Adaptor Command'
