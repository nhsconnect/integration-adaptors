from unittest import TestCase
from unittest.mock import MagicMock, patch
from mhs_common.workflow import sync_async_resynchroniser as resync

from utilities import test_utilities


PARTY_ID = "PARTY-ID"


class TestSyncAsyncWorkflow(TestCase):
    pass


class TestSyncAsyncReSynchroniser(TestCase):

    @test_utilities.async_test
    async def test_resync_happy(self):
        store = MagicMock()
        store.get.return_value = test_utilities.awaitable(True)
        resynchroniser = resync.SyncAsyncResynchroniser(store, 20, 1)

        result = await resynchroniser.pause_request('Message')
        self.assertTrue(result)

    @patch('tornado.gen.sleep')
    @test_utilities.async_test
    async def test_resync_no_response(self, sleep_mock):
        store = MagicMock()
        sleep_mock.return_value = test_utilities.awaitable(1)
        store.get.return_value = test_utilities.awaitable(None)
        resynchroniser = resync.SyncAsyncResynchroniser(store, 20, 1000)

        with self.assertRaises(resync.SyncAsyncResponseException):
            await resynchroniser.pause_request('Message')

        self.assertEqual(sleep_mock.call_count, 20)
        self.assertEqual(store.get.call_count, 20)
