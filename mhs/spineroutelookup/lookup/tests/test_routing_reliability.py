import unittest

from utilities.test_utilities import async_test

import lookup.dictionary_cache as dict_cache
import lookup.mhs_attribute_lookup as mhs_attribute_lookup
import lookup.routing_reliability as rar
import lookup.sds_exception as sds_exception
import lookup.tests.ldap_mocks as mocks

PARTY_KEY = " AP4RTY-K33Y"
INTERACTION_ID = "urn:nhs:names:services:psis:MCCI_IN010000UK13"
ODS_CODE = "ODSCODE1"

EXPECTED_ROUTING = {
    'nhsMhsFQDN': 'vpn-client-1411.opentest.hscic.gov.uk',
    'nhsMHSEndPoint': ['https://vpn-client-1411.opentest.hscic.gov.uk/'],
    'nhsMHSPartyKey': 'AP4RTY-K33Y',
    'nhsMhsCPAId': 'S918999410559',
    'uniqueIdentifier': ['918999199084']
}

EXPECTED_RELIABILITY = {
    'nhsMHSSyncReplyMode': 'MSHSignalsOnly',
    'nhsMHSRetries': '2',
    'nhsMHSPersistDuration': 'PT5M',
    'nhsMHSAckRequested': 'always',
    'nhsMHSDuplicateElimination': 'always',
    'nhsMHSRetryInterval': 'PT1M'
}


class TestRoutingAndReliability(unittest.TestCase):

    def setUp(self):
        cache = dict_cache.DictionaryCache()
        handler = mhs_attribute_lookup.MHSAttributeLookup(mocks.mocked_sds_client(), cache)
        self.router = rar.RoutingAndReliability(handler)

    @async_test
    async def test_get_routing(self):
        mhs_route_details = await self.router.get_end_point(ODS_CODE, INTERACTION_ID)
        self.assertEqual(mhs_route_details, EXPECTED_ROUTING)

    @async_test
    async def test_get_routing_bad_ods_code(self):
        with self.assertRaises(sds_exception.SDSException):
            await self.router.get_end_point("bad code", INTERACTION_ID)

    @async_test
    async def test_get_routing_bad_interaction_id(self):
        with self.assertRaises(sds_exception.SDSException):
            await self.router.get_end_point(ODS_CODE, "bad interaction")

    @async_test
    async def test_get_reliability(self):
        reliability_details = await self.router.get_reliability(ODS_CODE, INTERACTION_ID)
        self.assertEqual(reliability_details, EXPECTED_RELIABILITY)

    @async_test
    async def test_get_reliability_bad_ods_code(self):
        with self.assertRaises(sds_exception.SDSException):
            await self.router.get_reliability("bad code", INTERACTION_ID)

    @async_test
    async def test_get_reliability_bad_interaction_id(self):
        with self.assertRaises(sds_exception.SDSException):
            await self.router.get_reliability(ODS_CODE, "whew")

    @async_test
    async def test_empty_handler(self):
        with self.assertRaises(ValueError):
            rar.RoutingAndReliability(None)
