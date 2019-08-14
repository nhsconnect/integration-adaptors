from unittest import TestCase
from unittest.mock import MagicMock, patch
import lookup.dictionary_cache as dc
import lookup.mhs_attribute_lookup as mhs_attribute_lookup
import lookup.tests.ldap_mocks as mocks
from utilities import test_utilities
from utilities.test_utilities import async_test


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
    'uniqueIdentifier': ['S918999410559']
}


class TestMHSAttributeLookup(TestCase):

    def setUp(self) -> None:
        self.cache = dc.DictionaryCache()

    @async_test
    async def test_get_endpoint(self):
        handler = mhs_attribute_lookup.MHSAttributeLookup(mocks.mocked_sds_client(), self.cache)
        attributes = await handler.retrieve_mhs_attributes(ODS_CODE, INTERACTION_ID)
        for key, value in expected_mhs_attributes.items():
            self.assertEqual(value, attributes[key])

        # Assert exact number of attributes
        self.assertEqual(len(attributes), len(expected_mhs_attributes))

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
        handler = mhs_attribute_lookup.MHSAttributeLookup(mocks.mocked_sds_client(), MagicMock())

        handler.cache.retrieve_mhs_attributes_value.return_value = test_utilities.awaitable(None)
        handler.cache.add_cache_value.return_value = test_utilities.awaitable(None)

        result = await handler.retrieve_mhs_attributes(ODS_CODE, INTERACTION_ID)

        handler.cache.add_cache_value.assert_called_with(ODS_CODE, INTERACTION_ID, result)

    @async_test
    async def test_sds_not_called_when_value_in_cache(self):
        await self.cache.add_cache_value("check", "not", "added")
        handler = mhs_attribute_lookup.MHSAttributeLookup(MagicMock(), self.cache)

        result = await handler.retrieve_mhs_attributes("check", "not")

        self.assertEqual(result, "added")
        handler.sds_client.assert_not_called()

    @patch('time.time')
    @async_test
    async def test_retrieving_cache_value_doesnt_reset_ttl(self, patched_time):
        cache = dc.DictionaryCache(expiry_time=3)
        patched_time.return_value = 1
        client = MagicMock()

        client.get_mhs_details.return_value = test_utilities.awaitable({'attributes': 'testData'})
        handler = mhs_attribute_lookup.MHSAttributeLookup(client, cache)

        await handler.cache.add_cache_value("check", "not", "added")  # value in cache for 3 seconds

        patched_time.return_value = 2  # Set time to something before the expiry
        await handler.retrieve_mhs_attributes("check", "not")  # This will come from the cache
        handler.sds_client.get_mhs_details.assert_not_called()

        patched_time.return_value = 4.1  # wait for the cache to expire
        await handler.retrieve_mhs_attributes("check", "not")  # This should expire in the cache and call sds

        handler.sds_client.get_mhs_details.assert_called_once()
