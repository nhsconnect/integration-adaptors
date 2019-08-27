from unittest import TestCase

from mhs_common.workflow import sync_async


class TestSyncAsyncWorkflow(TestCase):
    def setUp(self):
        self.workflow = sync_async.SyncAsyncWorkflow()
