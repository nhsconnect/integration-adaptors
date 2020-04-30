import unittest
from datetime import datetime, timezone

from edifact.edifact_exception import EdifactValidationException
from edifact.outgoing.models.message import MessageHeader, MessageTrailer, BeginningOfMessage, NameAndAddress, \
    DateTimePeriod, ReferenceTransactionType, ReferenceTransactionNumber, SegmentGroup
from edifact.outgoing.models.segment import Segment
from edifact.outgoing.models.tests.base_segment_test import BaseSegmentTest


class TestMessageHeader(BaseSegmentTest, unittest.TestCase):
    """
    Test the generating of a message header
    """

    def _create_segment(self) -> Segment:
        return MessageHeader(sequence_number=1)

    def _get_attributes(self):
        return ['sequence_number']

    def _get_expected_edifact(self):
        return "UNH+00000001+FHSREG:0:1:FH:FHS001'"


class TestMessageTrailer(BaseSegmentTest, unittest.TestCase):
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


class TestNameAndAddress(BaseSegmentTest, unittest.TestCase):

    def _create_segment(self) -> Segment:
        return NameAndAddress(NameAndAddress.QualifierAndCode.FHS, 'PARTY')

    def _get_attributes(self):
        return ['qualifier', 'code', 'identifier']

    def _get_expected_edifact(self):
        return "NAD+FHS+PARTY:954'"


class TestDateTimePeriod(BaseSegmentTest, unittest.TestCase):

    TS = datetime(year=2020, month=4, day=28, hour=20, minute=58, tzinfo=timezone.utc)

    def _create_segment(self) -> Segment:
        return DateTimePeriod(DateTimePeriod.TypeAndFormat.TRANSLATION_TIMESTAMP, self.TS)

    def _get_attributes(self):
        return ['type_code', 'format_code', 'date_time_format', 'timestamp']

    def _get_expected_edifact(self):
        return "DTM+137:202004282058:203'"


class TestReferenceTransactionType(BaseSegmentTest, unittest.TestCase):
    def _create_segment(self) -> Segment:
        return ReferenceTransactionType(ReferenceTransactionType.TransactionType.ACCEPTANCE)

    def _get_attributes(self):
        return ['qualifier', 'reference']

    def _get_expected_edifact(self):
        return "RFF+950:G1'"


class TestReferenceTransactionNumber(BaseSegmentTest, unittest.TestCase):
    def _create_segment(self) -> Segment:
        return ReferenceTransactionNumber('1234')

    def _get_attributes(self):
        return ['qualifier', 'reference']

    def _get_expected_edifact(self):
        return "RFF+TN:1234'"


class TestSegmentGroup(unittest.TestCase):

    def test_to_edifact(self):
        self.assertEqual("S01+1'", SegmentGroup(1).to_edifact())
        self.assertEqual("S02+2'", SegmentGroup(2).to_edifact())

    def test_missing_segment_group_number(self):
        sg = SegmentGroup(1)
        sg.segment_group_number = None
        with self.assertRaises(EdifactValidationException, msg=f'missing "segment_group_number" did not fail validation') as ctx:
            sg.to_edifact()
        self.assertEqual(f'S: Attribute segment_group_number is required', ctx.exception.args[0])

    def test_segment_group_number_is_not_integer(self):
        sg = SegmentGroup('1')
        with self.assertRaises(EdifactValidationException, msg=f'missing "segment_group_number" did not fail validation') as ctx:
            sg.to_edifact()
        self.assertEqual(f'S: Attribute segment_group_number must be an integer', ctx.exception.args[0])

    def test_segment_group_number_is_out_of_range(self):
        sg = SegmentGroup(3)
        with self.assertRaises(EdifactValidationException, msg=f'missing "segment_group_number" did not fail validation') as ctx:
            sg.to_edifact()
        self.assertEqual(f'S: Attribute segment_group_number must be 1 or 2', ctx.exception.args[0])
