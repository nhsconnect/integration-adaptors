from unittest import TestCase
import mhs.routing.sds_handler as sds

import mhs.routing.tests.ldap_mocks as mocks
from utilities.test_utilities import async_test

NHS_SERVICES_BASE = "ou=services, o=nhs"

MHS_OBJECT_CLASS = "nhsMhs"

OPENTEST_SDS_URL = "192.168.128.11"
PARTY_KEY = " AP4RTY-K33Y"
SERVICE_ID = "urn:nhs:names:services:psis:MCCI_IN010000UK13"
ODS_CODE = "ODSCODE1"


# A91461
expected_mhs_attributes = {
    'nhsEPInteractionType': 'HL7',
    'nhsIDCode': 'ODSCODE1',
    'nhsMHSAckRequested': 'always',
    'nhsMHSActor': ['urn:oasis:names:tc:ebxml-msg:actor:toPartyMSH'],
    'nhsMHSDuplicateElimination': 'always',
    'nhsMHSEndPoint': ['https://vpn-client-1411.opentest.hscic.gov.uk/'],
    'nhsMHSIsAuthenticated': 'transient',
    'nhsMHSPartyKey': 'AP4RTY-K33Y',
    'nhsMHSPersistDuration': 'PT5M',
    'nhsMHSRetries': '2',
    'nhsMHSRetryInterval': 'PT1M',
    'nhsMHSSyncReplyMode': 'MSHSignalsOnly',
    'nhsMHsIN': 'MCCI_IN010000UK13',
    'nhsMHsSN': 'urn:nhs:names:services:psis',
    # 'nhsMhsCPAId': 'S918999410559', # Exclude this value since there seems to be two responses causing errors on this
    'nhsMhsFQDN': 'vpn-client-1411.opentest.hscic.gov.uk',
    'nhsMhsSvcIA': 'urn:nhs:names:services:psis:MCCI_IN010000UK13',
    'nhsProductKey': '7374',
    # 'uniqueIdentifier': ['S918999410559']
}


class TestMHSAttributeLookupHandler(TestCase):
    opentest_expected_reliability = {'nhsMHSAckRequested': 'always',
                                     'nhsMHSDuplicateElimination': 'always',
                                     'nhsMHSPersistDuration': 'PT5M',
                                     'nhsMHSRetries': '2',
                                     'nhsMHSRetryInterval': 'PT1M'}

    @async_test
    async def test_get_endpoint(self):
        handler = sds.MHSAttributeLookupHandler()
        handler.sds_client = mocks.mocked_sds_client()
        attributes = await handler.retrieve_mhs_attributes(ODS_CODE, SERVICE_ID)
        for key, value in expected_mhs_attributes.items():
            self.assertEqual(value, attributes[key])

        # Assert exact number of attributes, minus the unique values
        self.assertEqual(len(attributes) - 2, len(expected_mhs_attributes))

    @async_test
    async def test_no_connection(self):
        handler = sds.MHSAttributeLookupHandler()
        with self.assertRaises(IOError):
            await handler.retrieve_mhs_attributes(ODS_CODE, SERVICE_ID)
