import unittest
from typing import Optional, Tuple
from unittest import mock

from utilities import test_utilities
from utilities.test_utilities import async_test

import mhs_common.state.work_description as wd
from mhs_common.workflow import common

SERVICE = 'service'
ACTION = 'action'
SERVICE_ID = SERVICE + ":" + ACTION
INTERACTION_DETAILS = {
    'service': SERVICE,
    'action': ACTION
}

MHS_END_POINT_KEY = 'nhsMHSEndPoint'
MHS_END_POINT_VALUE = "example.com"
MHS_TO_PARTY_KEY_KEY = 'nhsMHSPartyKey'
MHS_TO_PARTY_KEY_VALUE = 'to-party-key'
MHS_CPA_ID_KEY = 'nhsMhsCPAId'
MHS_CPA_ID_VALUE = 'cpa-id'


class DummyCommonWorkflow(common.CommonWorkflow):
    async def handle_outbound_message(self, message_id: str, correlation_id: str, interaction_details: dict,
                                      payload: str, work_description_object: Optional[wd.WorkDescription]
                                      ) -> Tuple[int, str]:
        pass

    async def handle_inbound_message(self, message_id: str, correlation_id: str, work_description: wd.WorkDescription,
                                     payload: str):
        pass


class TestCommonWorkflow(unittest.TestCase):
    def setUp(self):
        self.mock_routing_reliability = mock.MagicMock()

        self.workflow = DummyCommonWorkflow(self.mock_routing_reliability)

    @async_test
    async def test_lookup_endpoint_details(self):
        self.mock_routing_reliability.get_end_point.return_value = test_utilities.awaitable({
            MHS_END_POINT_KEY: [MHS_END_POINT_VALUE],
            MHS_TO_PARTY_KEY_KEY: MHS_TO_PARTY_KEY_VALUE,
            MHS_CPA_ID_KEY: MHS_CPA_ID_VALUE
        })

        url, to_party_key, cpa_id = await self.workflow._lookup_endpoint_details(INTERACTION_DETAILS)

        self.mock_routing_reliability.get_end_point.assert_called_with(SERVICE_ID)
        self.assertEqual(url, MHS_END_POINT_VALUE)
        self.assertEqual(to_party_key, MHS_TO_PARTY_KEY_VALUE)
        self.assertEqual(cpa_id, MHS_CPA_ID_VALUE)

    @async_test
    async def test_lookup_endpoint_details_error(self):
        self.mock_routing_reliability.get_end_point.side_effect = Exception()

        with self.assertRaises(Exception):
            await self.workflow._lookup_endpoint_details(INTERACTION_DETAILS)

    @async_test
    async def test_extract_endpoint_url_no_endpoints_returned(self):
        endpoint_details = {MHS_END_POINT_KEY: []}

        with self.assertRaises(IndexError):
            common.CommonWorkflow._extract_endpoint_url(endpoint_details)

    @async_test
    async def test_extract_endpoint_url_multiple_endpoints_returned(self):
        expected_url = "first_url"
        endpoint_details = {MHS_END_POINT_KEY: [expected_url, "second-url"]}

        actual_url = common.CommonWorkflow._extract_endpoint_url(endpoint_details)

        self.assertEqual(expected_url, actual_url)
