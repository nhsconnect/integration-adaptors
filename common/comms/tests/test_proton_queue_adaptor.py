import asyncio
import unittest
from unittest.mock import patch

import tornado

import utilities.test_utilities
from comms.proton_queue_adaptor import ProtonQueueAdaptor
from utilities.test_utilities import async_test

TEST_MESSAGE = "TEST MESSAGE"
TEST_QUEUE_HOST = "TEST QUEUE HOST"


class TestProtonQueueAdaptor(unittest.TestCase):

    def setUp(self) -> None:
        self.service = ProtonQueueAdaptor(host=TEST_QUEUE_HOST)

    # TESTING SEND ASYNC METHOD
    @patch.object(tornado.ioloop.IOLoop, "current")
    @async_test
    async def test_send_async_success(self, mock_io_loop):
        mock_io_loop.run_in_executor.return_value = asyncio.Future()
        await self.service.send_async(TEST_MESSAGE)
