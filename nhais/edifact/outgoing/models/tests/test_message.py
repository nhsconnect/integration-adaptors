import unittest

from edifact.outgoing.models.message import MessageHeader, MessageTrailer, BeginningOfMessage, NameAndAddress
from edifact.outgoing.models.segment import Segment
from edifact.outgoing.models.tests.base_segment_test import BaseSegmentTest


class TestMessageHeader(BaseSegmentTest):
    """
    Test the generating of a message header
    """

    def _create_segment(self) -> Segment:
        return MessageHeader(sequence_number=1)

    def _get_attributes(self):
        return ['sequence_number']

    def _get_expected_edifact(self):
        return "UNH+00000001+FHSREG:0:1:FH:FHS001'"


class TestMessageTrailer(BaseSegmentTest):
    """
    Test the generating of a message trailer
    """

    def _create_segment(self) -> Segment:
        return MessageTrailer(number_of_segments=5, sequence_number=1)

    def _get_attributes(self):
        return ['number_of_segments', 'sequence_number']

    def _get_expected_edifact(self):
        return "UNT+5+00000001'"


class TestBeginningOfMessage(unittest.TestCase):

    def test_to_edifact(self):
        self.assertEqual("BGM+++507'", BeginningOfMessage().to_edifact())


class TestNameAndAddress(BaseSegmentTest):

    def _create_segment(self) -> Segment:
        return NameAndAddress(NameAndAddress.QualifierAndCode.FHS, 'PARTY')

    def _get_attributes(self):
        return ['qualifier', 'code', 'identifier']

    def _get_expected_edifact(self):
        return "NAD+FHS+PARTY:954'"
