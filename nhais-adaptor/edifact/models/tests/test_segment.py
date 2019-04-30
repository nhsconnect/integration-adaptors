import unittest
from edifact.models.segment import Segment


class TestSegment(unittest.TestCase):
    """
    Tests the generating of edifact segment
    """

    def test_convert_segment_to_edifact(self):
        segment = Segment(key="AAA", value="SOME_VALUE").to_edifact()
        self.assertEqual(segment, "AAA+SOME_VALUE'")

    def test_values_are_converted_to_upper_case(self):
        segment = Segment(key="AAA", value="some_value").to_edifact()
        self.assertEqual(segment, "AAA+SOME_VALUE'")

