"""Module for testing the Proton queue adaptor functionality."""
import unittest.mock

import comms.proton_queue_adaptor
import utilities.test_utilities

TEST_UUID = "TEST UUID"
TEST_MESSAGE = "TEST MESSAGE"
TEST_PROPERTIES = {'test-property-name': 'test-property-value'}
TEST_PROTON_MESSAGE = unittest.mock.Mock()
TEST_QUEUE_HOST = "TEST QUEUE HOST"
TEST_EXCEPTION = Exception()
TEST_SIDE_EFFECT = unittest.mock.Mock(side_effect=TEST_EXCEPTION)


@unittest.mock.patch('utilities.message_utilities.MessageUtilities.get_uuid', new=lambda: TEST_UUID)
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
        awaitable = self.service.send_async(TEST_MESSAGE)
        self.assertFalse(self.mock_container.return_value.run.called)

        await awaitable

        self.assert_proton_called_correctly()

    @utilities.test_utilities.async_test
    async def test_send_async_with_properties_success(self):
        """Test happy path of send_async."""
        awaitable = self.service.send_async(TEST_MESSAGE, properties=TEST_PROPERTIES)
        self.assertFalse(self.mock_container.return_value.run.called)

        await awaitable

        self.assert_proton_called_correctly(properties=TEST_PROPERTIES)

    # TESTING SEND SYNC METHOD

    def test_send_success(self):
        """Test happy path of send_sync."""

        self.service.send_sync(TEST_MESSAGE)

        self.assert_proton_called_correctly()

    def test_send_with_properties_success(self):
        """Test happy path of send_sync."""

        self.service.send_sync(TEST_MESSAGE, properties=TEST_PROPERTIES)

        self.assert_proton_called_correctly(properties=TEST_PROPERTIES)

    def assert_proton_called_correctly(self, properties=None):
        self.assertTrue(self.mock_container.return_value.run.called)
        proton_messaging_handler = self.mock_container.call_args[0][0]
        self.assertEqual(TEST_QUEUE_HOST, proton_messaging_handler._host)
        self.assertEqual(TEST_MESSAGE, proton_messaging_handler._message.body)
        self.assertEqual(TEST_UUID, proton_messaging_handler._message.id)
        self.assertEqual(properties, proton_messaging_handler._message.properties)


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
