import unittest
from unittest import mock
from mhs_common.workflow import synchronous as sync
from mhs_common import workflow
from mhs_common.state import work_description
from utilities import test_utilities
from utilities.test_utilities import async_test

PARTY_KEY = "313"


class TestSynchronousWorkflow(unittest.TestCase):

    def setUp(self) -> None:
        self.wd_store = mock.MagicMock()
        self.transmission = mock.MagicMock()
        self.routing_mock = mock.MagicMock()
        self.wf = sync.SynchronousWorkflow(
            PARTY_KEY,
            work_description_store=self.wd_store,
            transmission=self.transmission,
            persistence_store_max_retries=3,
            routing=self.routing_mock
        )

    @mock.patch('mhs_common.state.work_description.create_new_work_description')
    @async_test
    async def test_store_status_set_to_received(self, wd_mock):
        try:
            await self.wf.handle_outbound_message(message_id="123",
                                                  correlation_id="qwe",
                                                  interaction_details={},
                                                  payload="nice message", work_description_object=None)
        except Exception:
            # Don't care for exceptions, just want to check the store is set correctly first
            pass

        wd_mock.assert_called_with(self.wd_store, "123", workflow.SYNC,
                                   work_description.MessageStatus.OUTBOUND_MESSAGE_RECEIVED)

    @mock.patch('mhs_common.state.work_description.create_new_work_description')
    @async_test
    async def test_asid_lookup_failure_set_store(self, wd_mock):
        wdo = mock.MagicMock()
        wdo.publish.return_value = test_utilities.awaitable(None)
        wd_mock.return_value = wdo
        self.wf._lookup_to_asid_details = mock.MagicMock()
        self.wf._lookup_to_asid_details.side_effect = Exception()
        wdo.set_outbound_status.return_value = test_utilities.awaitable(None)

        error, text = await self.wf.handle_outbound_message(message_id="123",
                                                            correlation_id="qwe",
                                                            interaction_details={},
                                                            payload="nice message", work_description_object=None)

        wdo.set_outbound_status.assert_called_with(work_description.MessageStatus.OUTBOUND_MESSAGE_PREPARATION_FAILED)
        self.assertEqual(error, 500)
        self.assertEqual(text, 'Error obtaining outbound url')

    async def test_prepare_message_failure(self):
        pass
