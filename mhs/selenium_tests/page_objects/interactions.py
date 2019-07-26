
from selenium_tests.page_objects.build_scr import build_scr
from selenium_tests.page_objects.callmhs import call_mhs


def process_request(interaction_name, asid, nhs_number, human_readable):
    # This will be expanded to accommodate other interactions...
    if interaction_name.lower() == 'gp_summary_upload':
        scr = build_scr(asid, nhs_number, human_readable)

        mhs_result = call_mhs(interaction_name, scr)
        return mhs_result
    else:
        return 'Unknown MHS Adaptor Command'
