import unittest
from edifact.models.interchange import Interchange


class InterchangeTest(unittest.TestCase):
    """
    Test the generating of edifact message
    """
    def test_interchange_header_edifact(self):
        interchange = Interchange("header").to_edifact()
        self.assertEqual(interchange, "AAA-header")


if __name__ == '__main__':
    unittest.main()

