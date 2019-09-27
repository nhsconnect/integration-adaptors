from copy import copy
from unittest import TestCase

from utilities.test_utilities import async_test

import lookup.sds_client as sds_client
import lookup.sds_exception as re
import lookup.tests.ldap_mocks as mocks

MHS_OBJECT_CLASS = "nhsMhs"

PARTY_KEY = "AP4RTY-K33Y"
ASID = "123456789"
INTERACTION_ID = "urn:nhs:names:services:psis:MCCI_IN010000UK13"
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
    'nhsMhsCPAId': 'S918999410559',
    'nhsMhsFQDN': 'vpn-client-1411.opentest.hscic.gov.uk',
    'nhsMhsSvcIA': 'urn:nhs:names:services:psis:MCCI_IN010000UK13',
    'nhsProductKey': '7374',
    'uniqueIdentifier': ['S918999410559'],
}


class TestSDSClient(TestCase):

    @async_test
    async def test_mhs_details_lookup(self):
        client = mocks.mocked_sds_client()

        result = await client._mhs_details_lookup(PARTY_KEY, INTERACTION_ID)
        attributes = result[0]['attributes']

        # Check attributes contents
        for key, value in expected_mhs_attributes.items():
            self.assertEqual(value, attributes[key])

        # Assert exact number of attributes
        self.assertEqual(len(attributes), len(expected_mhs_attributes))

    @async_test
    async def test_accredited(self):
        client = mocks.mocked_sds_client()

        result = await client._accredited_system_lookup(ODS_CODE, INTERACTION_ID)

        self.assertIsNotNone(result)
        self.assertEqual(result[0]['attributes']['nhsMHSPartyKey'], PARTY_KEY)
        self.assertEqual(result[0]['attributes']['uniqueIdentifier'][0], ASID)
        self.assertEqual(len(result[0]['attributes']), 2)

    @async_test
    async def test_get_mhs_lookup(self):
        client = mocks.mocked_sds_client()

        attributes = await client.get_mhs_details(ODS_CODE, INTERACTION_ID)
        expected = copy(expected_mhs_attributes)
        expected['uniqueIdentifier'] = ['123456789']
        # check values present
        for key, value in expected.items():
            self.assertEqual(value, attributes[key])

        # Assert exact number of attributes, minus the unique values
        self.assertEqual(len(attributes), len(expected_mhs_attributes))

    @async_test
    async def test_should_return_result_as_dictionary(self):
        client = mocks.mocked_sds_client()

        attributes = await client.get_mhs_details(ODS_CODE, INTERACTION_ID)

        self.assertIsInstance(attributes, dict)

    @async_test
    async def test_no_results(self):
        client = mocks.mocked_sds_client()
        with self.assertRaises(re.SDSException):
            await client.get_mhs_details("fake code", "fake interaction")

    @async_test
    async def test_should_raise_error_if_no_connection_set(self):
        with self.assertRaises(ValueError):
            sds_client.SDSClient(None, "ou=search,o=base")

    @async_test
    async def test_should_raise_error_if_no_search_base_set(self):
        with self.assertRaises(ValueError):
            sds_client.SDSClient(mocks.fake_ldap_connection(), None)
