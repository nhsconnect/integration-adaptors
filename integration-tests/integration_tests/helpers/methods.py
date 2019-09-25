import os
from pathlib import Path

from utilities.file_utilities import FileUtilities

from test_definitions import ROOT_DIR


def get_asid():
    """ Looks up the asid from the environment settings

    The asid should be set in the 'Environment variables' section of the Run/Debug Configurations
        if this is not set, it will read from 'asid.txt' (excluded from the repo)
        or default to '123456789012' if 'asid.txt' is not found
    """
    try:
        asid_file = str(Path(ROOT_DIR) / "integration_tests/data/certs/asid.txt")
        asid = FileUtilities.get_file_string(asid_file)
    except:
        asid = None

    return os.environ.get('INTEGRATION_TEST_ASID', asid)


def get_mhs_hostname():
    """ Looks up the mhs hostname from the environment settings

    The mhs hostname should be set in the 'Environment variables' section of the Run/Debug Configurations
        if this is not set, it will default to 'localhost'
    """
    return "http://" + os.environ.get('MHS_ADDRESS', 'localhost') + "/"


def get_scr_hostname():
    """
    Looks up the hostname of the SCR from the environment variables
    
    :return: 
    """
    return os.environ.get('SCR_ADDRESS')

