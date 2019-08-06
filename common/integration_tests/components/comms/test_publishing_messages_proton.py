import unittest

import utilities.test_utilities
from comms.proton_queue_adaptor import ProtonQueueAdaptor
from integration_tests.components.reference_data import environment_config

TEST_MESSAGE = "TEST MESSAGE"


class TestProtonQueueAdaptor(unittest.TestCase):
    def setUp(self) -> None:
        self.service = ProtonQueueAdaptor(host=environment_config.get_message_queue_host())

    @utilities.test_utilities.async_test
    async def test_send_async(self):
        await self.service.send_async(TEST_MESSAGE)

    def test_send_sync(self):
        self.service.send_sync(TEST_MESSAGE)
