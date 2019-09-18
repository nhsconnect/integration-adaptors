import unittest
from unittest import mock
from message_handling import message_handler as mh
from builder.pystache_message_builder import MessageGenerationError


class TestMessageHandler(unittest.TestCase):

    @mock.patch('scr.gp_summary_update.SummaryCareRecord.populate_template_with_json_string')
    def test_call(self, template_mock):
        handler = mh.MessageHandler()
        input_json = "{'check': 'one'}"
        handler.forward_message_to_mhs(input_json)
        template_mock.assert_called_with(input_json)

    @mock.patch('scr.gp_summary_update.SummaryCareRecord.populate_template_with_json_string')
    def test_exception_raised_during_population(self, template_mock):
        template_mock.side_effect = MessageGenerationError('Exception')
        handler = mh.MessageHandler()
        input_json = "{'check': 'one'}"

        with self.assertRaises(MessageGenerationError) as e:
            handler.forward_message_to_mhs(input_json)
            self.assertEqual(str(e), 'Exception')
