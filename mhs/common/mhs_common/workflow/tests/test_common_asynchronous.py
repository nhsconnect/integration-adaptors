import unittest
from typing import Optional, Tuple
from unittest import mock

import mhs_common.state.work_description as wd
from mhs_common.workflow import common_asynchronous
from mhs_common.workflow.common import MessageData
from utilities import test_utilities
from utilities.test_utilities import async_test

SERVICE = 'service'
ACTION = 'action'
ODS_CODE = 'some-code'
SERVICE_ID = SERVICE + ":" + ACTION
INTERACTION_DETAILS = {
    'service': SERVICE,
    'action': ACTION
}

EXPECTED_RELIABILITY_DETAILS = {
    "nhsMHSSyncReplyMode": "MSHSignalsOnly"
}


class DummyCommonAsynchronousWorkflow(common_asynchronous.CommonAsynchronousWorkflow):
    async def handle_outbound_message(self, asid: str,  message_id: str, correlation_id: str, interaction_details: dict,
                                      payload: str, work_description_object: Optional[wd.WorkDescription]
                                      ) -> Tuple[int, str]:
        pass

    async def handle_inbound_message(self,
                                     message_id: str,
                                     correlation_id: str,
                                     work_description: wd.WorkDescription,
                                     message_data: MessageData):
        pass

    async def set_successful_message_response(self, wdo: wd.WorkDescription):
        pass

    async def set_failure_message_response(self, wdo: wd.WorkDescription):
        pass


class TestCommonAsynchronousWorkflow(unittest.TestCase):
    def setUp(self):
        party_key = 'PARTY_KEY'
        persistence_store = mock.MagicMock()
        transmission = mock.MagicMock()
        queue_adaptor = mock.MagicMock()
        max_request_size = 5000
        self.mock_routing_reliability = mock.MagicMock()

        self.workflow = DummyCommonAsynchronousWorkflow(party_key,
                                                        persistence_store,
                                                        transmission,
                                                        queue_adaptor,
                                                        max_request_size,
                                                        self.mock_routing_reliability)

    @async_test
    async def test_lookup_reliability_details(self):
        self.mock_routing_reliability.get_reliability.return_value = test_utilities.awaitable(
            EXPECTED_RELIABILITY_DETAILS)

        reliability_details = await self.workflow._lookup_reliability_details(INTERACTION_DETAILS, ODS_CODE)

        self.mock_routing_reliability.get_reliability.assert_called_with(SERVICE_ID, ODS_CODE)
        self.assertEqual(reliability_details, EXPECTED_RELIABILITY_DETAILS)

    @async_test
    async def test_lookup_reliability_details_error(self):
        self.mock_routing_reliability.get_reliability.side_effect = Exception()

        with self.assertRaises(Exception):
            await self.workflow._lookup_reliability_details(INTERACTION_DETAILS)
