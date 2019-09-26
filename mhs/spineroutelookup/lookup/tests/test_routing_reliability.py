import unittest
from unittest import mock

from utilities import test_utilities
from utilities.test_utilities import async_test

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
    'uniqueIdentifier': ['123456789']
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

    @async_test
    async def test_get_routing(self):
        router = self._configure_routing_and_reliability()

        mhs_route_details = await router.get_end_point(ODS_CODE, INTERACTION_ID)

        self.assertEqual(mhs_route_details, EXPECTED_ROUTING)

    @async_test
    async def test_get_routing_bad_ods_code(self):
        router = self._configure_routing_and_reliability()

        with self.assertRaises(sds_exception.SDSException):
            await router.get_end_point("bad code", INTERACTION_ID)

    @async_test
    async def test_get_routing_bad_interaction_id(self):
        router = self._configure_routing_and_reliability()

        with self.assertRaises(sds_exception.SDSException):
            await router.get_end_point(ODS_CODE, "bad interaction")

    @async_test
    async def test_get_reliability(self):
        router = self._configure_routing_and_reliability()

        reliability_details = await router.get_reliability(ODS_CODE, INTERACTION_ID)

        self.assertEqual(reliability_details, EXPECTED_RELIABILITY)

    @async_test
    async def test_get_reliability_bad_ods_code(self):
        router = self._configure_routing_and_reliability()

        with self.assertRaises(sds_exception.SDSException):
            await router.get_reliability("bad code", INTERACTION_ID)

    @async_test
    async def test_get_reliability_bad_interaction_id(self):
        router = self._configure_routing_and_reliability()

        with self.assertRaises(sds_exception.SDSException):
            await router.get_reliability(ODS_CODE, "whew")

    @async_test
    async def test_empty_handler(self):
        with self.assertRaises(ValueError):
            rar.RoutingAndReliability(None)

    @staticmethod
    def _configure_routing_and_reliability():
        cache = mock.Mock()
        cache.add_cache_value.return_value = test_utilities.awaitable(None)
        cache.retrieve_mhs_attributes_value.return_value = test_utilities.awaitable(None)
        handler = mhs_attribute_lookup.MHSAttributeLookup(mocks.mocked_sds_client(), cache)
        router = rar.RoutingAndReliability(handler)
        return router
