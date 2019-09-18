"""Module that relates to the general processing of an inbound message"""
import unittest
from unittest import mock
from message_handling import message_forwarder as mh
from builder.pystache_message_builder import MessageGenerationError


class TestMessageForwarder(unittest.TestCase):
    """Tests associated with the MessageForwarder class"""

    def test_forwarding_message_attempts_to_populate_message_template(self):
        template_mock = mock.MagicMock()
        interactions_map = {'interaction': template_mock}

        handler = mh.MessageForwarder(interactions_map)
        input_json = {'check': 'one'}
        handler.forward_message_to_mhs('interaction', input_json)
        template_mock.populate_template.assert_called_with(input_json)

    def test_exception_raised_during_population_is_raised(self):
        template_mock = mock.MagicMock()
        template_mock.populate_template.side_effect = MessageGenerationError('Exception')

        interactions_map = {'interaction': template_mock}
        handler = mh.MessageForwarder(interactions_map)
        input_json = {'check': 'one'}

        with self.assertRaises(MessageGenerationError) as e:
            handler.forward_message_to_mhs('interaction', input_json)
            self.assertEqual(str(e), 'Exception')

    def test_exception_raised_if_no_message_template_populator_found(self):
        handler = mh.MessageForwarder({})
        input_json = {'check': 'one'}

        with self.assertRaises(MessageGenerationError) as e:
            handler.forward_message_to_mhs('interaction', input_json)
            self.assertEqual(str(e), 'Failed to find interaction with interaction name: interaction')
