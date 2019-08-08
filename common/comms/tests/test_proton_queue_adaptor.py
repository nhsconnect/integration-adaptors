"""Module for testing the Proton queue adaptor functionality."""
import asyncio
import unittest.mock

import comms.proton_queue_adaptor
import utilities.test_utilities

TEST_MESSAGE = "TEST MESSAGE"
TEST_PROTON_MESSAGE = unittest.mock.Mock()
TEST_QUEUE_HOST = "TEST QUEUE HOST"
TEST_EXCEPTION = Exception()
TEST_SIDE_EFFECT = unittest.mock.Mock(side_effect=TEST_EXCEPTION)


class TestProtonQueueAdaptor(unittest.TestCase):
    """Class to contain tests for the ProtonQueueAdaptor functionality."""

    def setUp(self) -> None:
        """Prepare standard mocks and service for unit testing."""
        patcher = unittest.mock.patch.object(comms.proton_queue_adaptor.proton.reactor, "Container")
        self.mock_container = patcher.start()
        self.addCleanup(patcher.stop)
        self.service = comms.proton_queue_adaptor.ProtonQueueAdaptor(host=TEST_QUEUE_HOST)

    # TESTING SEND ASYNC METHOD
    @utilities.test_utilities.async_test
    async def test_send_async_success(self):
        """Test happy path of send_async."""
        self.mock_container.return_value.run.return_value = asyncio.Future()

        await self.service.send_async(TEST_MESSAGE)

        self.assertTrue(self.mock_container.return_value.run.called)

    # TESTING SEND SYNC METHOD
    def test_send_success(self):
        """Test happy path of send_sync."""

        self.service.send_sync(TEST_MESSAGE)

        self.assertTrue(self.mock_container.return_value.run.called)


class TestProtonMessagingHandler(unittest.TestCase):
    """Class to contain tests for the ProtonMessagingHandler functionality."""

    def setUp(self) -> None:
        """Prepare service for testing."""
        self.handler = comms.proton_queue_adaptor.ProtonMessagingHandler(TEST_QUEUE_HOST, TEST_PROTON_MESSAGE)

    # TESTING STARTUP METHOD
    def test_on_start_success(self):
        """Test happy path of on_start."""
        mock_event = unittest.mock.MagicMock()

        self.handler.on_start(mock_event)

        self.assertTrue(mock_event.container.create_sender.called)

    def test_on_start_error(self):
        """Test error condition when creating a message sender."""
        mock_event = unittest.mock.MagicMock()
        mock_event.container.create_sender.side_effect = TEST_SIDE_EFFECT

        with self.assertRaises(Exception) as ex:
            self.handler.on_start(mock_event)

        self.assertIs(ex.exception, TEST_EXCEPTION)
        self.assertTrue(mock_event.container.create_sender.called)

    # TESTING SENDABLE METHOD
    def test_on_sendable_success(self):
        """Test happy path for on_sendable."""
        mock_event = unittest.mock.MagicMock()
        mock_event.sender.credit = True
        self.handler._sent = False

        self.handler.on_sendable(mock_event)

        self.assertTrue(mock_event.sender.send.called)
        self.assertTrue(self.handler._sent)

    def test_on_sendable_already_sent(self):
        """Test on_sendable when message has already been sent (and not rejected)."""
        mock_event = unittest.mock.MagicMock()
        mock_event.sender.credit = True
        self.handler._sent = True

        self.handler.on_sendable(mock_event)

        self.assertFalse(mock_event.sender.send.called)
        self.assertTrue(self.handler._sent)

    def test_on_sendable_no_credit(self):
        """Test unhappy path when on_sendable is invoked but there is no sending credit."""
        mock_event = unittest.mock.MagicMock()
        mock_event.sender.credit = False
        self.handler._sent = False

        with self.assertRaises(comms.proton_queue_adaptor.MessageSendingError):
            self.handler.on_sendable(mock_event)

        self.assertFalse(mock_event.sender.send.called)
        self.assertFalse(self.handler._sent)

    def test_on_sendable_error(self):
        """Test unhappy path where performing the send action raises an exception."""
        mock_event = unittest.mock.MagicMock()
        mock_event.sender.credit = True
        mock_event.sender.send.side_effect = TEST_SIDE_EFFECT
        self.handler._sent = False

        with self.assertRaises(Exception) as ex:
            self.handler.on_sendable(mock_event)

        self.assertIs(ex.exception, TEST_EXCEPTION)
        self.assertTrue(mock_event.sender.send.called)
        self.assertFalse(self.handler._sent)

    # TESTING ACCEPTED METHOD
    def test_on_accepted_success(self):
        """Test happy path for on_accepted."""
        mock_event = unittest.mock.MagicMock()

        self.handler.on_accepted(mock_event)

        self.assertTrue(mock_event.connection.close.called)

    def test_on_accepted_error(self):
        """Test unhappy path when attempting to close the connection raises an exception."""
        mock_event = unittest.mock.MagicMock()
        mock_event.connection.close.side_effect = TEST_SIDE_EFFECT

        with self.assertRaises(Exception) as ex:
            self.handler.on_accepted(mock_event)

        self.assertIs(ex.exception, TEST_EXCEPTION)

    # TESTING DISCONNECT METHOD
    def test_on_disconnected_success(self):
        """Test happy path for disconnecting from the host."""
        mock_event = unittest.mock.MagicMock()
        self.handler._sent = True

        self.handler.on_disconnected(mock_event)

    def test_on_disconnected_early(self):
        """Test unhappy path when disconnecting from the host occurs too early."""
        mock_event = unittest.mock.MagicMock()

        with self.assertRaises(comms.proton_queue_adaptor.EarlyDisconnectError):
            self.handler.on_disconnected(mock_event)

    # TESTING REJECTED METHOD
    def test_on_rejected(self):
        """Test happy path allowing for a message to be rejected by the host (and ultimately re-submitted)."""
        mock_event = unittest.mock.MagicMock()
        self.handler._sent = True

        self.handler.on_rejected(mock_event)

        self.assertFalse(self.handler._sent)
