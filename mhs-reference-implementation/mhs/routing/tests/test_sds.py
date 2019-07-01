from unittest import TestCase
import mhs.routing.sds as sds
import mhs.routing.tests.ldap_mocks as mocks
from utilities.test_utilities import async_test
import mhs.routing.routing_exception as re

NHS_SERVICES_BASE = "ou=services, o=nhs"

MHS_OBJECT_CLASS = "nhsMhs"

PARTY_KEY = "AP4RTY-K33Y"
SERVICE_ID = "urn:nhs:names:services:psis:MCCI_IN010000UK13"
ODS_CODE = "ODSCODE1"


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


class TestSDSClient(TestCase):

    @async_test
    async def test_mhs_details_lookup(self):
        client = mocks.mocked_sds_client()

        result = await client._mhs_details_lookup(PARTY_KEY, SERVICE_ID)
        attributes = result[0]['attributes']

        # Check attributes contents
        for key, value in expected_mhs_attributes.items():
            self.assertEqual(value, attributes[key])

        self.assertIsNotNone(attributes['uniqueIdentifier'])
        self.assertIsNotNone(attributes['nhsMhsCPAId'])

        # Assert exact number of attributes
        self.assertEqual(len(expected_mhs_attributes) + 2, len(attributes))

    @async_test
    async def test_accredited(self):
        client = mocks.mocked_sds_client()

        result = await client._accredited_system_lookup(ODS_CODE, SERVICE_ID)
        self.assertIsNotNone(result)
        self.assertIsNotNone(result[0]['attributes']['nhsMHSPartyKey'] == 'A91461-9199084')
        self.assertEqual(len(result[0]['attributes']), 1)

    @async_test
    async def test_get_mhs_lookup(self):
        client = mocks.mocked_sds_client()

        attributes = await client.get_mhs_details(ODS_CODE, SERVICE_ID)

        # check values present
        for key, value in expected_mhs_attributes.items():
            self.assertEqual(value, attributes[key])

        # Assert exact number of attributes, minus the unique values
        self.assertEqual(len(attributes) - 2, len(expected_mhs_attributes))

    @async_test
    async def test_no_results(self):
        client = mocks.mocked_sds_client()
        with self.assertRaises(re.RoutingException):
            await client.get_mhs_details("fake code", "fake interaction")

    @async_test
    async def test_accredited_no_connection(self):
        client = sds.SDSClient()
        with self.assertRaises(IOError):
            await client._accredited_system_lookup(ODS_CODE, SERVICE_ID)

    @async_test
    async def test_get_mhs_lookup_no_connection(self):
        client = sds.SDSClient()
        with self.assertRaises(IOError):
            await client._mhs_details_lookup(ODS_CODE, SERVICE_ID)
