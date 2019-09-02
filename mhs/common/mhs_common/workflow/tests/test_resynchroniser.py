from unittest import TestCase
from unittest.mock import MagicMock
from mhs_common.workflow import sync_async_resynchroniser as resync
from mhs_common.state import work_description as wd
from utilities import test_utilities


PARTY_ID = "PARTY-ID"


class TestSyncAsyncWorkflow(TestCase):
    pass


class TestSyncAsyncReSynchroniser(TestCase):

    @test_utilities.async_test
    async def test_resync_happy(self):
        store = MagicMock()
        store.get = test_utilities.awaitable({''})
        resynchroniser = resync.SyncAsyncResynchroniser()
