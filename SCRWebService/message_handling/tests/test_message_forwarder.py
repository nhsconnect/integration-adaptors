"""Module that relates to the general processing of an inbound message"""
import unittest
from unittest import mock
from message_handling import message_forwarder as mh
from builder.pystache_message_builder import MessageGenerationError
from utilities.test_utilities import async_test, awaitable


class TestMessageForwarder(unittest.TestCase):
    """Tests associated with the MessageForwarder class"""

    @async_test
    async def test_forwarding_message_attempts_to_populate_message_template(self):
        template_mock = mock.MagicMock()
        sender_mock = mock.MagicMock()
        sender_mock.send_message_to_mhs.return_value = awaitable("response")
        interactions_map = {'interaction': template_mock}

        handler = mh.MessageForwarder(interactions_map, sender_mock)
        input_json = {'check': 'one'}
        await handler.forward_message_to_mhs('interaction', input_json, None, None)
        template_mock.populate_template.assert_called_with(input_json)

    @async_test
    async def test_exceptions_raised_during_message_population_are_caught_and_raised_as_MessageGenerationError(self):
        template_mock = mock.MagicMock()
        sender_mock = mock.MagicMock()
        template_mock.populate_template.side_effect = Exception('Exception')

        interactions_map = {'interaction': template_mock}
        handler = mh.MessageForwarder(interactions_map, sender_mock)
        input_json = {'check': 'one'}

        with self.assertRaises(MessageGenerationError) as e:
            await handler.forward_message_to_mhs('interaction', input_json, None, None)
            self.assertEqual(str(e), 'Exception')

    @async_test
    async def test_exception_raised_if_no_message_template_populator_found(self):
        sender_mock = mock.MagicMock()
        handler = mh.MessageForwarder({}, sender_mock)
        input_json = {'check': 'one'}

        with self.assertRaises(MessageGenerationError) as e:
            await handler.forward_message_to_mhs('interaction', input_json, None, None)
            self.assertEqual(str(e), 'Failed to find interaction with interaction name: interaction')
