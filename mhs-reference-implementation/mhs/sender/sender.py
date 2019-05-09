import copy
import logging

from mhs.builder.ebxml_message_builder import CONVERSATION_ID, FROM_PARTY_ID
from mhs.builder.ebxml_request_message_builder import MESSAGE
from utilities.message_utilities import MessageUtilities

PARTY_ID = "A91424-9199121"

WRAPPER_REQUIRED = 'ebxml_wrapper_required'


class UnknownInteractionError(Exception):
    """Raised when an unknown interaction has been specified"""

    def __init__(self, interaction_name):
        """Create a new UnknownInteractionError for the specified interaction name.

        :param interaction_name: The interaction name requested but not found.
        """
        self.interaction_name = interaction_name


class Sender:
    def __init__(self, interactions_config, message_builder, transport):
        """Create a new Sender that uses the specified dependencies to load config, build a message and send it.

        :param interactions_config: The object that can be used to obtain interaction-specific configuration details.
        :param message_builder: The message builder that can be used to build a message.
        :param transport: The transport that can be used to send messages.
        """

        self.interactions_config = interactions_config
        self.message_builder = message_builder
        self.transport = transport

    def send_message(self, interaction_name, message_to_send):
        """Send the specified message for the interaction named.

        :param interaction_name: The name of the interaction the message is related to.
        :param message_to_send: A string representing the message to be sent.
        :return: The content of the response received when the message was sent.
        :raises: An UnknownInteractionError if the interaction_name specified was not found.
        """

        interaction_details = self.interactions_config.get_interaction_details(interaction_name)
        if not interaction_details:
            raise UnknownInteractionError(interaction_name)

        requires_ebxml_wrapper = interaction_details[WRAPPER_REQUIRED]
        if requires_ebxml_wrapper:
            message = self._wrap_message_in_ebxml(interaction_details, message_to_send)
        else:
            message = message_to_send

        response = self.transport.make_request(interaction_details, message)

        return response

    def _wrap_message_in_ebxml(self, interaction_details, message_to_send):
        """Wrap the specified message in an ebXML wrapper.

        :param interaction_details: The interaction configuration to use when building the ebXML wrapper.
        :param message_to_send: The message to be sent.
        :return: A string representing the message wrapped in the generated ebXML wrapper.
        """
        context = copy.deepcopy(interaction_details)
        context[FROM_PARTY_ID] = PARTY_ID

        conversation_id = MessageUtilities.get_uuid()
        context[CONVERSATION_ID] = conversation_id
        logging.debug("Generated ebXML wrapper with conversation ID: %s", conversation_id)

        context[MESSAGE] = message_to_send
        return self.message_builder.build_message(context)
