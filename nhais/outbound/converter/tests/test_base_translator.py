import unittest

from outbound.converter.base_translator import BaseFhirToEdifactTranslator
from utilities.test_utilities import async_test


class TestBaseFhirToEdifactTranslator(unittest.TestCase):

    @async_test
    async def test_message_translated(self):
        patient = {}
        translator = BaseFhirToEdifactTranslator()
        edifact = await translator.convert(patient)
        self.assertIsNotNone(edifact)
        self.assertTrue(len(edifact) > 0)
        print(edifact)
