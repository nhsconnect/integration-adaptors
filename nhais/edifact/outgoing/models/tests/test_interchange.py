import unittest
from datetime import datetime

from edifact.outgoing.models.interchange import InterchangeHeader, InterchangeTrailer
from edifact.outgoing.models.segment import Segment
from edifact.outgoing.models.tests.base_segment_test import BaseSegmentTest


class TestInterchangeHeader(BaseSegmentTest, unittest.TestCase):

    TS = datetime(year=2019, month=4, day=23, hour=9, minute=0)

    def _create_segment(self) -> Segment:
        return InterchangeHeader(sender="SNDR", recipient="RECP", date_time=self.TS, sequence_number=1)

    def _get_attributes(self):
        return ['sender', 'recipient', 'date_time', 'sequence_number']

    def _get_expected_edifact(self):
        return "UNB+UNOA:2+SNDR+RECP+190423:0900+00000001'"


class TestInterchangeTrailer(BaseSegmentTest, unittest.TestCase):

    def _create_segment(self) -> Segment:
        return InterchangeTrailer(number_of_messages=1, sequence_number=1)

    def _get_attributes(self):
        return ['number_of_messages', 'sequence_number']

    def _get_expected_edifact(self):
        return "UNZ+1+00000001'"
