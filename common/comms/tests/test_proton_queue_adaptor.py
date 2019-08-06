import asyncio
import unittest.mock

import proton

import comms.proton_queue_adaptor
import utilities.test_utilities

TEST_MESSAGE = "TEST MESSAGE"
TEST_QUEUE_HOST = "TEST QUEUE HOST"
TEST_EXCEPTION = Exception()
TEST_SIDE_EFFECT = unittest.mock.Mock(side_effect=TEST_EXCEPTION)


class TestProtonQueueAdaptor(unittest.TestCase):

    def setUp(self) -> None:
        self.service = comms.proton_queue_adaptor.ProtonQueueAdaptor(host=TEST_QUEUE_HOST)
        self.handler = comms.proton_queue_adaptor.ProtonMessagingHandler(TEST_QUEUE_HOST, TEST_MESSAGE)

    # -- Service Tests
    # TESTING SEND ASYNC METHOD
    @unittest.mock.patch.object(proton.reactor, "Container")
    @utilities.test_utilities.async_test
    async def test_send_async_success(self, mock_container):
        mock_container.run.return_value = asyncio.Future()
        await self.service.send_async(TEST_MESSAGE)

    # TESTING SEND SYNC METHOD
    @unittest.mock.patch.object(proton.reactor, "Container")
    def test_send_success(self, mock_container):
        self.service.send_sync(TEST_MESSAGE)

    # -- Handler Tests
    # TESTING STARTUP METHOD
    def test_on_start_success(self):
        mock_event = unittest.mock.MagicMock()

        self.handler.on_start(mock_event)

        self.assertTrue(mock_event.container.create_sender.called)

    def test_on_start_error(self):
        mock_event = unittest.mock.MagicMock()
        mock_event.container.create_sender.side_effect = TEST_SIDE_EFFECT

        with self.assertRaises(Exception) as ex:
            self.handler.on_start(mock_event)

        self.assertIs(ex.exception, TEST_EXCEPTION)
        self.assertTrue(mock_event.container.create_sender.called)

    # TESTING SENDABLE METHOD
    def test_on_sendable_success(self):
        mock_event = unittest.mock.MagicMock()
        mock_event.sender.credit = True
        self.handler.sent = False

        self.handler.on_sendable(mock_event)

        self.assertTrue(mock_event.sender.send.called)
        self.assertTrue(self.handler.sent)

    def test_on_sendable_already_sent(self):
        mock_event = unittest.mock.MagicMock()
        mock_event.sender.credit = True
        self.handler.sent = True

        self.handler.on_sendable(mock_event)

        self.assertFalse(mock_event.sender.send.called)
        self.assertTrue(self.handler.sent)

    def test_on_sendable_no_credit(self):
        mock_event = unittest.mock.MagicMock()
        mock_event.sender.credit = False
        self.handler.sent = False

        with self.assertRaises(comms.proton_queue_adaptor.MessageSendingError):
            self.handler.on_sendable(mock_event)

        self.assertFalse(mock_event.sender.send.called)
        self.assertFalse(self.handler.sent)

    def test_on_sendable_error(self):
        mock_event = unittest.mock.MagicMock()
        mock_event.sender.credit = True
        mock_event.sender.send.side_effect = TEST_SIDE_EFFECT
        self.handler.sent = False

        with self.assertRaises(Exception) as ex:
            self.handler.on_sendable(mock_event)

        self.assertIs(ex.exception, TEST_EXCEPTION)
        self.assertTrue(mock_event.sender.send.called)
        self.assertFalse(self.handler.sent)

    # TESTING ACCEPTED METHOD
    def test_on_accepted_success(self):
        mock_event = unittest.mock.MagicMock()

        self.handler.on_accepted(mock_event)

        self.assertTrue(mock_event.connection.close.called)

    def test_on_accepted_error(self):
        mock_event = unittest.mock.MagicMock()
        mock_event.connection.close.side_effect = TEST_SIDE_EFFECT

        with self.assertRaises(Exception) as ex:
            self.handler.on_accepted(mock_event)

        self.assertIs(ex.exception, TEST_EXCEPTION)

    # TESTING DISCONNECT METHOD
    def test_on_disconnected_success(self):
        mock_event = unittest.mock.MagicMock()
        self.handler.sent = True

        self.handler.on_disconnected(mock_event)

    def test_on_disconnected_early(self):
        mock_event = unittest.mock.MagicMock()

        with self.assertRaises(comms.proton_queue_adaptor.EarlyDisconnectError):
            self.handler.on_disconnected(mock_event)

    # TESTING REJECTED METHOD
    def test_on_rejected(self):
        mock_event = unittest.mock.MagicMock()
        self.handler.sent = True

        self.handler.on_rejected(mock_event)

        self.assertFalse(self.handler.sent)
