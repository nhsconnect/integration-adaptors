import os
from pathlib import Path
from unittest import TestCase

import mhs_common.configuration.configuration_manager as configuration_manager

TEST_CONFIG_DIR = "test_config"
INTERACTIONS_JSON = "interactions.json"

INTERACTION_NAME = "test_interaction"
PROPERTY_NAME = "property"
PROPERTY_VALUE = "value"


class TestConfigurationManager(TestCase):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    interactions_config_file = str(Path(current_dir) / TEST_CONFIG_DIR / INTERACTIONS_JSON)

    def setUp(self):
        self.interactions_config_file = configuration_manager.ConfigurationManager(self.interactions_config_file)

    def test_get_interaction_details(self):
        details = self.interactions_config_file.get_interaction_details(INTERACTION_NAME)

        self.assertEqual(details[PROPERTY_NAME], PROPERTY_VALUE)

    def test_get_interaction_details_returns_copy(self):
        first_details = self.interactions_config_file.get_interaction_details(INTERACTION_NAME)
        first_details['test'] = 'blah'

        second_details = self.interactions_config_file.get_interaction_details(INTERACTION_NAME)

        self.assertNotIn('test', second_details)
