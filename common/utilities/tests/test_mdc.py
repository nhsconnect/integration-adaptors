from unittest import TestCase

from utilities import mdc


class TestMDC(TestCase):

    def setUp(self):
        self._clearMDC()

    def tearDown(self):
        self._clearMDC()

    @staticmethod
    def _clearMDC():
        mdc.message_id.set(None)
        mdc.correlation_id.set(None)
        mdc.interaction_id.set(None)
        mdc.inbound_message_id.set(None)

    def test_build_tracking_header_with_all_values(self):
        mdc.message_id.set('1')
        mdc.correlation_id.set('2')
        mdc.interaction_id.set('3')
        mdc.inbound_message_id.set('4')

        headers = mdc.build_tracking_headers()

        self.assertEqual(len(headers.keys()), 4)
        self.assertEqual(headers['Message-Id'], '1')
        self.assertEqual(headers['Correlation-Id'], '2')
        self.assertEqual(headers['Interaction-Id'], '3')
        self.assertEqual(headers['Inbound-Message-Id'], '4')

    def test_build_tracking_header_with_some_values(self):
        mdc.message_id.set('1')
        mdc.inbound_message_id.set('4')

        headers = mdc.build_tracking_headers()

        self.assertEqual(len(headers.keys()), 2)
        self.assertEqual(headers['Message-Id'], '1')
        self.assertEqual(headers['Inbound-Message-Id'], '4')

    def test_build_tracking_header_with_no_values(self):
        headers = mdc.build_tracking_headers()

        self.assertIsNone(headers)
