"""This module defines the sync-async workflow."""

import copy
import logging
from typing import Tuple, Optional, Dict

import mhs.common.configuration.configuration_manager as configuration_manager
import mhs.common.messages.ebxml_envelope as ebxml_envelope
import mhs.common.messages.ebxml_request_envelope as ebxml_request_envelope
import mhs.common.workflow.common as common
import mhs.common.workflow.common_synchronous as common_synchronous
import mhs.outbound.transmission.outbound_transmission as outbound_transmission
import utilities.message_utilities as message_utilities

ASYNC_RESPONSE_EXPECTED = 'async_response_expected'


class SyncAsyncWorkflow(common_synchronous.CommonSynchronousWorkflow):
    """Handles the workflow for the sync-async messaging pattern."""

    def __init__(self, config_manager: configuration_manager.ConfigurationManager,
                 transmission: outbound_transmission.OutboundTransmission, party_id: str):
        """Create a new SyncAsyncWorkflow that uses the specified dependencies to load config, build a message and
        send it.

        :param config_manager: The object that can be used to obtain configuration details.
        :param transmission: The component that can be used to send messages.
        :param party_id: The party ID of this MHS. Sent in ebXML requests.
        """

        self.config_manager = config_manager
        self.transmission = transmission
        self.party_id = party_id

    def prepare_message(self, interaction_name: str, content: str, message_id: Optional[str] = None) \
            -> Tuple[bool, str, str]:
        """Prepare a message to be sent for the specified interaction. Wraps the provided content if required.

        :param interaction_name: The name of the interaction the message is related to.
        :param content: The message content to be sent.
        :param message_id: message id to use in the message header. If not supplied, we generate a new message id.
        The purpose of this param is to be used for duplicate elimination when sending async messages.
        :return: A tuple containing:
        1. A flag indicating whether this message should be sent asynchronously
        2. the ID of the message, if an asynchronous response is expected, otherwise None
        3. The message to send
        """
        interaction_details = self._get_interaction_details(interaction_name)

        if message_id is not None:
            interaction_details[ebxml_envelope.MESSAGE_ID] = message_id

        is_async = interaction_details[ASYNC_RESPONSE_EXPECTED]
        if is_async:
            message_id, message = self._wrap_message_in_ebxml(interaction_details, content)
        else:
            message_id = None
            message = content

        return is_async, message_id, message

    def send_message(self, interaction_name: str, message: str) -> str:
        """Send the provided message for the interaction named. Returns the response received immediately, but note that
        if the interaction will result in an asynchronous response, this will simply be the acknowledgement of the
        request.

        :param interaction_name: The name of the interaction the message is related to.
        :param message: A string representing the message to be sent.
        :return: A string containing the immediate response to the message sent.
        :raises: An UnknownInteractionError if the interaction_name specified was not found.
        """

        interaction_details = self._get_interaction_details(interaction_name)
        response = self.transmission.make_request(interaction_details, message)
        logging.debug("Message sent. Received response: %s", response)
        return response

    def _get_interaction_details(self, interaction_name):
        interaction_details = self.config_manager.get_interaction_details(interaction_name)

        if not interaction_details:
            raise common.UnknownInteractionError(interaction_name)

        return interaction_details

    def _wrap_message_in_ebxml(self, interaction_details: Dict[str, str], content: str) \
            -> Tuple[str, str]:
        """Wrap the specified message in an ebXML wrapper.

        :param interaction_details: The interaction configuration to use when building the ebXML wrapper.
        :param content: The message content to be sent.
        :return: A tuple of strings representing the ID and the content of the message wrapped in the generated ebXML
        wrapper.
        """
        context = copy.deepcopy(interaction_details)
        context[ebxml_envelope.FROM_PARTY_ID] = self.party_id

        conversation_id = message_utilities.MessageUtilities.get_uuid()
        context[ebxml_envelope.CONVERSATION_ID] = conversation_id

        context[ebxml_request_envelope.MESSAGE] = content
        request = ebxml_request_envelope.EbxmlRequestEnvelope(context)

        message_id, message = request.serialize()

        logging.debug("Generated ebXML wrapper with conversation ID '%s' and message ID '%s'", conversation_id,
                      message_id)
        return message_id, message
