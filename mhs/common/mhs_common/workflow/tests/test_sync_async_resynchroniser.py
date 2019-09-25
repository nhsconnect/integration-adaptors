from unittest import TestCase
from unittest.mock import MagicMock, patch
from mhs_common.workflow import sync_async_resynchroniser as resync

from utilities import test_utilities


PARTY_ID = "PARTY-ID"


class TestSyncAsyncWorkflow(TestCase):
    pass


class TestSyncAsyncReSynchroniser(TestCase):

    @test_utilities.async_test
    async def test_should_return_correct_result_on_resynchronisation(self):
        # Arrange
        store = MagicMock()
        store.get.return_value = test_utilities.awaitable(True)
        resynchroniser = resync.SyncAsyncResynchroniser(store, 20, 1, 0)

        # Act
        result = await resynchroniser.pause_request('Message')

        # Assert
        self.assertEqual(store.get.call_count, 1)
        self.assertTrue(result)

    @patch('asyncio.sleep')
    @test_utilities.async_test
    async def test_should_respect_max_retries_while_attempting_to_retry(self, sleep_mock):
        # Arrange
        store = MagicMock()
        sleep_mock.return_value = test_utilities.awaitable(1)
        store.get.side_effect = [test_utilities.awaitable(None), test_utilities.awaitable(True)]
        resynchroniser = resync.SyncAsyncResynchroniser(store, 20, 1, 0)

        # Act
        response = await resynchroniser.pause_request('Message')

        # Assert
        self.assertTrue(response)
        self.assertEqual(store.get.call_count, 2)

    @patch('asyncio.sleep')
    @test_utilities.async_test
    async def test_should_perform_correct_number_of_sleeps_between_retries(self, sleep_mock):
        # Arrange
        store = MagicMock()
        sleep_mock.return_value = test_utilities.awaitable(1)
        store.get.return_value = test_utilities.awaitable(None)
        resynchroniser = resync.SyncAsyncResynchroniser(store, 20, 1, 0)

        # Act
        with self.assertRaises(resync.SyncAsyncResponseException):
            await resynchroniser.pause_request('Message')

        # Assert
        self.assertEqual(sleep_mock.call_count, 20)

    @patch('asyncio.sleep')
    @test_utilities.async_test
    async def test_should_initially_wait_before_polling_store(self, sleep_mock):
        # Arrange
        store = MagicMock()
        sleep_mock.return_value = test_utilities.awaitable(1)
        store.get.return_value = test_utilities.awaitable(True)
        resynchroniser = resync.SyncAsyncResynchroniser(store, 20, 1, 5)

        # Act
        await resynchroniser.pause_request('Message')

        # Assert
        self.assertEqual(sleep_mock.call_count, 1)
        self.assertEqual(sleep_mock.call_args[0][0], 5)
