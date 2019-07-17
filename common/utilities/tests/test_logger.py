import io
import logging
import sys
from unittest import TestCase
from unittest.mock import patch
import re

from common.utilities import logger


class TestLogger(TestCase):

    def test_dictionary_formatting(self):
        # Tests both removing the spaces and surrounding values with quotes if needed
        input_dict = {
            'Key With Space': 'value with space',
            'EasyKey': 'EasyValue'
        }

        expected_output = {
            'Key With Space': 'KeyWithSpace="value with space"',
            'EasyKey': 'EasyKey=EasyValue'
        }
        output = logger._format_values_in_map(input_dict)
        self.assertEqual(output, expected_output)

    @patch('sys.stdout', new_callable=io.StringIO)
    def test_audit(self, mock_std):
        logger.load_global_log_config()
        logger.Logger('TES') \
            .info('{There Will Be No Spaces Today}', {'There Will Be No Spaces Today': 'wow qwe'}, correlation_id=2)

        output = mock_std.getvalue()
        output_dict = dict(re.findall(r'(\S+)=(".*?"|\S+)', output))
        self.assertEqual(output_dict['CorrelationId'], "2")
        self.assertEqual(output_dict["ThereWillBeNoSpacesToday"], '"wow qwe"')

    @patch('sys.stdout', new_callable=io.StringIO)
    def test_format_and_write(self, mock_std):
        logger.load_global_log_config()
        logger.Logger()._format_and_write(
            message="{yes} {no} {maybe}",
            values={'yes': 'one', 'no': 'two', 'maybe': 'three'},
            request_id=10,
            correlation_id=5,
            level=50,
            process_key_num="100"
        )

        output = mock_std.getvalue()
        output_dict = dict(re.findall(r'(\S+)=(".*?"|\S+)', output))
        self.assertEqual(output_dict['yes'], "one")
        self.assertEqual(output_dict["no"], 'two')
