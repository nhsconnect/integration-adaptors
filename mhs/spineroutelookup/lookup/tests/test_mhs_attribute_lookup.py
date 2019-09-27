from unittest import TestCase
from unittest import mock

from utilities import test_utilities
from utilities.test_utilities import async_test

import lookup.mhs_attribute_lookup as mhs_attribute_lookup
import lookup.tests.ldap_mocks as mocks

NHS_SERVICES_BASE = "ou=services, o=nhs"

MHS_OBJECT_CLASS = "nhsMhs"

OPENTEST_SDS_URL = "192.168.128.11"
PARTY_KEY = " AP4RTY-K33Y"
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
    'uniqueIdentifier': ['123456789']
}


class TestMHSAttributeLookup(TestCase):

    def setUp(self) -> None:
        self.cache = mock.MagicMock()

    @async_test
    async def test_get_endpoint(self):
        self.cache.retrieve_mhs_attributes_value.return_value = test_utilities.awaitable(None)
        self.cache.add_cache_value.return_value = test_utilities.awaitable(None)
        handler = mhs_attribute_lookup.MHSAttributeLookup(mocks.mocked_sds_client(), self.cache)

        attributes = await handler.retrieve_mhs_attributes(ODS_CODE, INTERACTION_ID)

        self.assertEqual(expected_mhs_attributes, attributes)

    @async_test
    async def test_no_client(self):
        with self.assertRaises(ValueError):
            mhs_attribute_lookup.MHSAttributeLookup(None, self.cache)

    @async_test
    async def test_no_cache(self):
        with self.assertRaises(ValueError):
            mhs_attribute_lookup.MHSAttributeLookup(mocks.mocked_sds_client(), None)

    @async_test
    async def test_value_added_to_cache(self):
        handler = mhs_attribute_lookup.MHSAttributeLookup(mocks.mocked_sds_client(), self.cache)
        self.cache.retrieve_mhs_attributes_value.return_value = test_utilities.awaitable(None)
        self.cache.add_cache_value.return_value = test_utilities.awaitable(None)

        result = await handler.retrieve_mhs_attributes(ODS_CODE, INTERACTION_ID)

        self.cache.add_cache_value.assert_called_with(ODS_CODE, INTERACTION_ID, result)

    @async_test
    async def test_sds_not_called_when_value_in_cache(self):
        expected_value = {"some-key": "some-value"}
        self.cache.retrieve_mhs_attributes_value.return_value = test_utilities.awaitable(expected_value)
        handler = mhs_attribute_lookup.MHSAttributeLookup(mock.MagicMock(), self.cache)

        result = await handler.retrieve_mhs_attributes(ODS_CODE, INTERACTION_ID)

        self.assertEqual(result, expected_value)
        handler.sds_client.assert_not_called()

    @async_test
    async def test_should_not_propagate_exception_when_retrieving_cache_entry(self):
        self.cache.retrieve_mhs_attributes_value.side_effect = Exception
        self.cache.add_cache_value.return_value = test_utilities.awaitable(None)
        handler = mhs_attribute_lookup.MHSAttributeLookup(mocks.mocked_sds_client(), self.cache)

        attributes = await handler.retrieve_mhs_attributes(ODS_CODE, INTERACTION_ID)

        self.assertEqual(expected_mhs_attributes, attributes)

    @async_test
    async def test_should_not_propagate_exception_when_storing_cache_entry(self):
        self.cache.retrieve_mhs_attributes_value.side_effect = test_utilities.awaitable(None)
        self.cache.add_cache_value.side_effect = None
        handler = mhs_attribute_lookup.MHSAttributeLookup(mocks.mocked_sds_client(), self.cache)

        attributes = await handler.retrieve_mhs_attributes(ODS_CODE, INTERACTION_ID)

        self.assertEqual(expected_mhs_attributes, attributes)
