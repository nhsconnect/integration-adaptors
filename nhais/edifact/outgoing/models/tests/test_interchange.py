import unittest
from datetime import datetime

from edifact.outgoing.models.interchange import InterchangeHeader, InterchangeTrailer, EdifactValidationException
from edifact.outgoing.models.tests.base_segment_test import test_missing_params

TS = datetime(year=2019, month=4, day=23, hour=9, minute=0)


class TestInterchangeHeader(unittest.TestCase):
    """
    Test the generating of an interchange header
    """

    def test_to_edifact(self):
        int_hdr = InterchangeHeader(sender="SNDR", recipient="RECP", date_time=TS, sequence_number=1).to_edifact()
        self.assertEqual(int_hdr, "UNB+UNOA:2+SNDR+RECP+190423:0900+00000001'")

    def test_missing_params(self):
        params = {
            'sender': "SNDR",
            'recipient': "RECP",
            'date_time': TS,
            'sequence_number': 1
        }
        test_missing_params(self, params, InterchangeHeader)


class TestInterchangeTrailer(unittest.TestCase):
    """
    Test the generating of an interchange trailer
    """

    def test_to_edifact(self):
        int_trl = InterchangeTrailer(number_of_messages=1, sequence_number=1).to_edifact()
        self.assertEqual(int_trl, "UNZ+1+00000001'")

    def test_missing_params(self):
        params = {
            'number_of_messages': 1,
            'sequence_number': 1
        }
        test_missing_params(self, params, InterchangeTrailer)
