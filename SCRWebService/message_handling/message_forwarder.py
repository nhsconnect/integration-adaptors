"""Module related to processing of an outbound message"""
from typing import Dict, Optional
from utilities import integration_adaptors_logger as log
from builder.pystache_message_builder import MessageGenerationError
from message_handling.message_sender import MessageSender
import xml.etree.ElementTree as ET

logger = log.IntegrationAdaptorsLogger(__name__)


class MessageSendingError(Exception):
    """Error raised during message sending"""

    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg


class MessageForwarder(object):
    """Class to provide message forwarding functionality, in particular hl7 message population is performed."""

    def __init__(self, interactions: dict, message_sender: MessageSender):
        """
        Constructor for the message forwarder
        :param interactions: A dictionary mapping human readable interaction names to the object that is responsible
        for populating the associated message template
        """
        self.interactions = interactions
        self.message_sender = message_sender

    async def forward_message_to_mhs(self, interaction_name: str,
                                     message_contents: Dict, 
                                     message_id: Optional[str],
                                     correlation_id: Optional[str]):

        """
        Handles forwarding a given interaction to the MHS, including populating the appropriate message template
        :param interaction_name: The human readable name associated with a particular interaction
        :param message_contents: The dictionary parsed from the json body
        :param correlation_id: 
        :param message_id: 
        :return: None
        """
        templator = self._get_interaction_template_populator(interaction_name)
        populated_message = self._populate_message_template(templator, message_contents)
        response = await self._send_message_to_mhs(interaction_id=templator.interaction_id,
                                                   message=populated_message, 
                                                   message_id=message_id,
                                                   correlation_id=correlation_id)
        return templator.parse_response(response)

    def _get_interaction_template_populator(self, interaction_name: str):
        """
        Retrieves the template populater object for the given interaction_name
        :param interaction_name: Human readable interaction id
        :return: A template populator
        """
        interaction_template_populator = self.interactions.get(interaction_name)
        if not interaction_template_populator:
            logger.error('Failed to find interaction templator for interaction name: {name}',
                         fparams={'name': interaction_name})
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
            logger.exception('Message generation failed')
            raise MessageGenerationError(str(e))

    async def _send_message_to_mhs(self, interaction_id: str,
                                   message: str,
                                   message_id: Optional[str],
                                   correlation_id: Optional[str]):
        """
        Using the message sender dependency, the generated message is forwarded to the mhs
        :param interaction_id: The interaction id used as part of the header
        :param message: hl7 message body
        :return: The response from the mhs of sending the
        """
        try:
            return await self.message_sender.send_message_to_mhs(interaction_id, message, message_id, correlation_id)
        except Exception as e:
            logger.exception('Exception raised during message sending')
            raise MessageSendingError(str(e))
