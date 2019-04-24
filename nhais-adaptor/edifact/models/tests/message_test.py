import unittest
from edifact.models.message import MessageHeader


class MessageHeaderTest(unittest.TestCase):
    """
    Test the generating of a message header
    """

    def test_message_header_to_edifact(self):
        msg_hdr = MessageHeader(sequence_number="00001").to_edifact()
        self.assertEqual(msg_hdr, "UNH+00001+FHSREG:0:1:FH:FHS001'")


if __name__ == '__main__':
    unittest.main()
