"""This module defines the configuration manager component."""
import copy

import utilities.file_utilities as file_utilities


class ConfigurationManager(object):
    """A utility used to obtain configuration details for the current application."""

    def __init__(self, interactions_file_name: str):
        """Create a new ConfigurationManager that loads the interaction details from the specified JSON file.

        :param interactions_file_name: The file to load interaction details from. This file should be in JSON format.
        """
        self.interactions = file_utilities.get_file_dict(interactions_file_name)

    def get_interaction_details(self, interaction_name: str) -> dict:
        """Get details for the specified interaction.

        :param interaction_name: The name of the interaction to retrieve details for.
        :return: A dictionary of interaction-specific details, or None if an entry for the specified name was not found.
        """
        return copy.deepcopy(self.interactions.get(interaction_name))
