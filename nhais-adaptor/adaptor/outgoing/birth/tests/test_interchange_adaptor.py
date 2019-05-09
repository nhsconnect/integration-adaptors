import unittest

import adaptor.outgoing.birth.tests.fixtures as fixtures
from testfixtures import compare
import adaptor.outgoing.interchange_adaptor as adaptor


class TestInterchangeAdaptor(unittest.TestCase):
    """
    Test the conversation of fhir to an edifact interchange for a birth registration
    """

    def test_create_interchange(self):
        """
        Test the function to create an edifact interchange
        """
        with self.subTest("When the operation is for a Birth Registration"):
            expected_edifact_interchange = ("UNB+UNOA:2+TES5+XX11+190423:0900+000001++FHSREG'"
                                            "UNH+000001+FHSREG:0:1:FH:FHS001'"
                                            "BGM+++507'"
                                            "NAD+FHS+XX1:954'"
                                            "DTM+137:201904230900:203'"
                                            "RFF+950:G1'"
                                            "S01+1'"
                                            "RFF+TN:17'"
                                            "NAD+GP+4826940,281:900'"
                                            "HEA+ACD+A:ZZZ'"
                                            "HEA+ATP+1:ZZZ'"
                                            "DTM+956:20190423:102'"
                                            "LOC+950+SPIDEY TOWN'"
                                            "S02+2'"
                                            "PNA+PAT+NHSNO11111:OPI+++SU:PARKER+FO:PETER+TI:MR'"
                                            "DTM+329:20190420:102'"
                                            "PDI+1'"
                                            "NAD+PAT++:1 SPIDEY WAY::SPIDEY TOWN:+++++SP1 1AA'"
                                            "UNT+18+000001'"
                                            "UNZ+1+000001'")

            op_def = fixtures.create_operation_definition_for_birth_registration()

            (sender, recipient, interchange_seq_no, interchange) = adaptor.create_interchange(fhir_operation=op_def)

            compare(interchange, expected_edifact_interchange)
