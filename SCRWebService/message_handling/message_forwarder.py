"""Module related to processing of an outbound message"""
from typing import Dict

from utilities import integration_adaptors_logger as log
from builder.pystache_message_builder import MessageGenerationError

logger = log.IntegrationAdaptorsLogger('MSG-HANDLER')


class MessageForwarder(object):
    """Class to provide message forwarding functionality, in particular hl7 message population is performed."""

    def __init__(self, interactions: dict):
        """
        Constructor for the message forwarder
        :param interactions: A dictionary mapping human readable interaction names to the object that is responsible
        for populating the associated message template
        """
        self.interactions = interactions

    def forward_message_to_mhs(self, interaction_name: str, message_contents: Dict):
        """
        Handles forwarding a given interaction to the MHS, including populating the appropriate message template
        :param interaction_name: The human readable name associated with a particular interaction
        :param message_contents: The dictionary parsed from the json body
        :return: None
        """
        template_populator = self._get_interaction_template_populator(interaction_name)
        populated_message = self._populate_message_template(template_populator, message_contents)

    def _get_interaction_template_populator(self, interaction_name: str):
        """
        Retrieves the template populater object for the given interaction_name
        :param interaction_name: Human readable interaction id
        :return: A template populator
        """
        interaction_template_populator = self.interactions.get(interaction_name)
        if not interaction_template_populator:
            logger.error('002', 'Failed to find interaction templater for interaction name: {name}', 
                         {'name': interaction_name})
            raise MessageGenerationError(f'Failed to find interaction with interaction name: {interaction_name}')
        return interaction_template_populator
    
    def _populate_message_template(self, template_populator, supplier_message_parameters: Dict) -> str:
        """
        Generates a hl7 message string from the parameters
        :param template_populator:
        :param supplier_message_parameters: The parameters to be populated into the message template
        :return: hl7 message string with the populated values
        """
        try:
            return template_populator.populate_template(supplier_message_parameters)
        except Exception as e:
            logger.error('001', 'Message generation failed {exception}', {'exception': e})
            raise MessageGenerationError(str(e))
