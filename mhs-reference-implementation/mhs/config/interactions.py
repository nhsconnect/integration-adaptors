from utilities.file_utilities import FileUtilities


class InteractionsConfigFile:
    def __init__(self, interactions_file_name):
        """Create a new InteractionsConfigFile that loads the interaction details from the specified JSON file.

        :param interactions_file_name: The file to load interaction details from. This file should be in JSON format.
        """
        self.interactions = FileUtilities.get_file_dict(interactions_file_name)

    def get_interaction_details(self, interaction_name):
        """Get details for the specified interaction.

        :param interaction_name: The name of the interaction to retrieve details for.
        :return: A dictionary of interaction-specific details.
        """
        interaction_details = self.interactions.get(interaction_name)

        if not interaction_details:
            raise Exception('Unknown interaction: {}'.format(interaction_name))

        return interaction_details
