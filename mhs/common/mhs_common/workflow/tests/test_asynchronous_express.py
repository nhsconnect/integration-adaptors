import unittest
from unittest import mock

import mhs_common.workflow.asynchronous_express as async_express


class TestAsynchronousExpressWorkflow(unittest.TestCase):
    def setUp(self):
        self.mock_persistence_store = mock.MagicMock()
        self.workflow = async_express.AsynchronousExpressWorkflow(self.mock_persistence_store)
