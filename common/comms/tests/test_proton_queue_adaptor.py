import unittest

import utilities.test_utilities
from comms.proton_queue_adaptor import ProtonQueueAdaptor

TEST_MESSAGE = "TEST MESSAGE"


class TestProtonQueueAdaptor(unittest.TestCase):
    def setUp(self) -> None:
        self.service = ProtonQueueAdaptor(host='http://127.0.0.1:5672/test2')

    @utilities.test_utilities.async_test
    async def test_send_async(self):
        await self.service.send_async(TEST_MESSAGE)

    def test_send_sync(self):
        self.service.send_sync(TEST_MESSAGE)
