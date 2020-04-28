import unittest

from edifact.outgoing.models.message import MessageHeader, MessageTrailer, EdifactValidationException, \
    BeginningOfMessage, NameAndAddress
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


class TestMessageTrailer(unittest.TestCase):
    """
    Test the generating of a message trailer
    """

    def test_message_trailer_to_edifact(self):
        msg_trl = MessageTrailer(number_of_segments=5, sequence_number=1).to_edifact()
        self.assertEqual(msg_trl, "UNT+5+00000001'")

    def test_missing_params(self):
        params = {
            'number_of_segments': 5,
            'sequence_number': 1
        }
        test_missing_params(self, params, MessageTrailer)


class TestBeginningOfMessage(unittest.TestCase):

    def test_to_edifact(self):
        self.assertEqual("BGM+++507'", BeginningOfMessage().to_edifact())


class TestNameAndAddress(unittest.TestCase):

    def test_to_edifact(self):
        self.assertEqual("NAD+FHS+PARTY:954'", NameAndAddress(NameAndAddress.QualifierAndCode.FHS, 'PARTY').to_edifact())

    def test_missing_properties(self):
        gen = lambda: NameAndAddress(NameAndAddress.QualifierAndCode.FHS, 'PARTY')
        test_missing_properties(self, ['qualifier', 'code', 'identifier'], gen)
