import os
from pathlib import Path
from unittest import TestCase

from mhs.config.interactions import InteractionsFile

TEST_CONFIG_DIR = "test_config"
INTERACTIONS_JSON = "interactions.json"

INTERACTION_NAME = "test_interaction"
PROPERTY_NAME = "property"
PROPERTY_VALUE = "value"


class TestInteractionsFile(TestCase):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    interactions_file = str(Path(current_dir) / TEST_CONFIG_DIR / INTERACTIONS_JSON)

    def setUp(self):
        self.interactions_file = InteractionsFile(self.interactions_file)

    def test_get_interaction_details(self):
        details = self.interactions_file.get_interaction_details(INTERACTION_NAME)

        self.assertEqual(details[PROPERTY_NAME], PROPERTY_VALUE)

    def test_get_interaction_details_incorrect_name(self):
        with (self.assertRaises(Exception)):
            self.interactions_file.get_interaction_details("invalid")
