"""Module for testing the Proton queue adaptor functionality."""
import unittest.mock

import comms.proton_queue_adaptor
import utilities.test_utilities

TEST_UUID = "TEST UUID"
TEST_MESSAGE = {'test': 'message'}
# Hardcoded serialisation as we use json.dumps in the code being tested, so want to avoid testing code with itself
TEST_MESSAGE_SERIALISED = '{"test": "message"}'
TEST_PROPERTIES = {'test-property-name': 'test-property-value'}
TEST_PROTON_MESSAGE = unittest.mock.Mock()
TEST_QUEUE_SINGLE_URL = ["URL"]
TEST_QUEUE_MULTIPLE_URLS = ["URL_1", "URL_2"]
TEST_QUEUE_NAME = "TEST QUEUE NAME"
TEST_QUEUE_USERNAME = "TEST QUEUE USERNAME"
TEST_QUEUE_PASSWORD = "TEST QUEUE PASSWORD"
TEST_EXCEPTION = Exception()
TEST_SIDE_EFFECT = unittest.mock.Mock(side_effect=TEST_EXCEPTION)


@unittest.mock.patch('utilities.message_utilities.get_uuid', new=lambda: TEST_UUID)
class TestProtonQueueAdaptor(unittest.TestCase):
    """Class to contain tests for the ProtonQueueAdaptor functionality."""

    def setUp(self) -> None:
        """Prepare standard mocks and service for unit testing."""
        patcher = unittest.mock.patch.object(comms.proton_queue_adaptor.proton.reactor, "Container")
        self.mock_container = patcher.start()
        self.addCleanup(patcher.stop)
        self.service = comms.proton_queue_adaptor.ProtonQueueAdaptor(
            urls=TEST_QUEUE_SINGLE_URL, queue=TEST_QUEUE_NAME, username=TEST_QUEUE_USERNAME, password=TEST_QUEUE_PASSWORD)

    def test_value_error_is_raised_when_broker_urls_are_invalid(self) -> None:
        test_data = [
            {"queue": TEST_QUEUE_NAME, "urls": None},
            {"queue": TEST_QUEUE_NAME, "urls": ""},
            {"queue": TEST_QUEUE_NAME, "urls": " "},
            {"urls": TEST_QUEUE_SINGLE_URL, "queue": None},
            {"urls": TEST_QUEUE_SINGLE_URL, "queue": ""},
            {"urls": TEST_QUEUE_SINGLE_URL, "queue": " "}
        ]

        for data in test_data:
            self.assertRaises(
                ValueError,
                comms.proton_queue_adaptor.ProtonQueueAdaptor,
                **data, username=None, password=None)

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

    def assert_proton_called_correctly(self, properties=None):
        self.assertTrue(self.mock_container.return_value.run.called)
        proton_messaging_handler = self.mock_container.call_args[0][0]
        self.assertEqual(TEST_QUEUE_SINGLE_URL[0], proton_messaging_handler._url)
        self.assertEqual(TEST_QUEUE_NAME, proton_messaging_handler._queue)
        self.assertEqual(TEST_QUEUE_USERNAME, proton_messaging_handler._username)
        self.assertEqual(TEST_QUEUE_PASSWORD, proton_messaging_handler._password)
        self.assertEqual(TEST_MESSAGE_SERIALISED, proton_messaging_handler._message.body)
        self.assertEqual(TEST_UUID, proton_messaging_handler._message.id)
        self.assertEqual(properties, proton_messaging_handler._message.properties)


@unittest.mock.patch('utilities.message_utilities.get_uuid', new=lambda: TEST_UUID)
class TestProtonQueueAdaptorRetries(unittest.TestCase):
    """Class to contain tests for the ProtonQueueAdaptor retry functionality."""

    def setUp(self) -> None:
        """Prepare standard mocks and service for unit testing."""
        patcher = unittest.mock.patch.object(comms.proton_queue_adaptor.proton.reactor, "Container")
        self.mock_container = patcher.start()
        self.addCleanup(patcher.stop)
        self.service = comms.proton_queue_adaptor.ProtonQueueAdaptor(
            urls=TEST_QUEUE_MULTIPLE_URLS,
            queue=TEST_QUEUE_NAME,
            username=TEST_QUEUE_USERNAME,
            password=TEST_QUEUE_PASSWORD,
            max_retries=1,
            retry_delay=0)

    # TESTING SEND ASYNC METHOD

    @utilities.test_utilities.async_test
    async def test_send_async_when_first_url_succeeds(self):
        """Test happy path of send_async."""
        awaitable = self.service.send_async(TEST_MESSAGE)
        self.assertFalse(self.mock_container.return_value.run.called)

        self.mock_container.return_value.run.side_effect = [
            None,
            comms.proton_queue_adaptor.EarlyDisconnectError()
        ]

        await awaitable

        self.assert_proton_called_correctly(TEST_QUEUE_MULTIPLE_URLS[0], call_index=0, call_count=1)

    @utilities.test_utilities.async_test
    async def test_send_async_when_first_url_fails(self):
        """Test happy path of send_async."""
        awaitable = self.service.send_async(TEST_MESSAGE)
        self.assertFalse(self.mock_container.return_value.run.called)

        self.mock_container.return_value.run.side_effect = [
            comms.proton_queue_adaptor.EarlyDisconnectError(),
            None
        ]

        await awaitable

        self.assert_proton_called_correctly(TEST_QUEUE_MULTIPLE_URLS[0], call_index=0, call_count=2)
        self.assert_proton_called_correctly(TEST_QUEUE_MULTIPLE_URLS[1], call_index=1, call_count=2)

    @utilities.test_utilities.async_test
    async def test_send_async_when_second_both_urls_fail_once(self):
        """Test happy path of send_async."""
        awaitable = self.service.send_async(TEST_MESSAGE)
        self.assertFalse(self.mock_container.return_value.run.called)

        side_effects = [
            comms.proton_queue_adaptor.EarlyDisconnectError(),
            comms.proton_queue_adaptor.EarlyDisconnectError(),
            None
        ]
        self.mock_container.return_value.run.side_effect = side_effects

        await awaitable

        self.assert_proton_called_correctly(TEST_QUEUE_MULTIPLE_URLS[0], call_index=0, call_count=len(side_effects))
        self.assert_proton_called_correctly(TEST_QUEUE_MULTIPLE_URLS[1], call_index=1, call_count=len(side_effects))
        self.assert_proton_called_correctly(TEST_QUEUE_MULTIPLE_URLS[0], call_index=2, call_count=len(side_effects))

    @utilities.test_utilities.async_test
    async def test_send_async_when_second_both_urls_fail_twice(self):
        """Test happy path of send_async."""
        awaitable = self.service.send_async(TEST_MESSAGE)
        self.assertFalse(self.mock_container.return_value.run.called)

        self.mock_container.return_value.run.side_effect = [comms.proton_queue_adaptor.EarlyDisconnectError() for _ in range(4)]

        with self.assertRaises(comms.proton_queue_adaptor.MessageSendingError):
            await awaitable

        self.assert_proton_called_correctly(TEST_QUEUE_MULTIPLE_URLS[0], call_index=0, call_count=4)
        self.assert_proton_called_correctly(TEST_QUEUE_MULTIPLE_URLS[1], call_index=1, call_count=4)
        self.assert_proton_called_correctly(TEST_QUEUE_MULTIPLE_URLS[0], call_index=2, call_count=4)
        self.assert_proton_called_correctly(TEST_QUEUE_MULTIPLE_URLS[1], call_index=3, call_count=4)

    def assert_proton_called_correctly(self, url, call_index, call_count):
        self.assertTrue(self.mock_container.return_value.run.called)
        self.assertEqual(self.mock_container.return_value.run.call_count, call_count)
        url_index = TEST_QUEUE_MULTIPLE_URLS.index(url)
        proton_messaging_handler = self.mock_container.call_args_list[call_index][0][0]
        self.assertEqual(TEST_QUEUE_MULTIPLE_URLS[url_index], proton_messaging_handler._url)
        self.assertEqual(TEST_QUEUE_NAME, proton_messaging_handler._queue)
        self.assertEqual(TEST_QUEUE_USERNAME, proton_messaging_handler._username)
        self.assertEqual(TEST_QUEUE_PASSWORD, proton_messaging_handler._password)
        self.assertEqual(TEST_MESSAGE_SERIALISED, proton_messaging_handler._message.body)
        self.assertEqual(TEST_UUID, proton_messaging_handler._message.id)


class TestProtonMessagingHandler(unittest.TestCase):
    """Class to contain tests for the ProtonMessagingHandler functionality."""

    def setUp(self) -> None:
        """Prepare service for testing."""
        self.handler = comms.proton_queue_adaptor.ProtonMessagingHandler(
            TEST_QUEUE_SINGLE_URL[0], TEST_QUEUE_NAME, TEST_QUEUE_USERNAME, TEST_QUEUE_PASSWORD, TEST_PROTON_MESSAGE)

    # TESTING STARTUP METHOD
    def test_on_start_success(self):
        """Test happy path of on_start."""
        mock_event = unittest.mock.MagicMock()

        conn_mock = unittest.mock.MagicMock()
        mock_event.container.connect.return_value = conn_mock

        self.handler.on_start(mock_event)

        mock_event.container.connect.assert_called_once_with(
            url=TEST_QUEUE_SINGLE_URL[0],
            user=TEST_QUEUE_USERNAME,
            password=TEST_QUEUE_PASSWORD,
            reconnect=False)
        mock_event.container.create_sender.assert_called_once_with(conn_mock, target=TEST_QUEUE_NAME)

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

    # TESTING ERROR HANDLING METHODS
    def test_should_raise_exception_on_error(self):
        error_handling_methods = [
            self.handler.on_transport_error,
            self.handler.on_connection_error,
            self.handler.on_session_error,
            self.handler.on_link_error
        ]

        for error_handling_method in error_handling_methods:
            with self.subTest(error_handling_method.__name__):
                mock_event = unittest.mock.MagicMock()

                with self.assertRaises(comms.proton_queue_adaptor.EarlyDisconnectError):
                    error_handling_method(mock_event)
