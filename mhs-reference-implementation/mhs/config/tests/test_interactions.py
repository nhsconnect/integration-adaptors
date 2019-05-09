import os
from pathlib import Path
from unittest import TestCase

from mhs.config.interactions import InteractionsConfigFile

TEST_CONFIG_DIR = "test_config"
INTERACTIONS_JSON = "interactions.json"

INTERACTION_NAME = "test_interaction"
PROPERTY_NAME = "property"
PROPERTY_VALUE = "value"


class TestInteractionsConfigFile(TestCase):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    interactions_config_file = str(Path(current_dir) / TEST_CONFIG_DIR / INTERACTIONS_JSON)

    def setUp(self):
        self.interactions_config_file = InteractionsConfigFile(self.interactions_config_file)

    def test_get_interaction_details(self):
        details = self.interactions_config_file.get_interaction_details(INTERACTION_NAME)

        self.assertEqual(details[PROPERTY_NAME], PROPERTY_VALUE)
