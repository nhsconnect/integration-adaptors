"""This module defines the sync-async workflow."""

import copy
import asyncio
from typing import Tuple, Dict
from utilities import integration_adaptors_logger as log, message_utilities
import mhs_common.messages.ebxml_envelope as ebxml_envelope
import mhs_common.messages.ebxml_request_envelope as ebxml_request_envelope
from mhs_common.state import work_description as wd
from mhs_common.transmission import transmission_adaptor as ta
from mhs_common.workflow import common_synchronous
from mhs_common.state import persistence_adaptor as pa

logger = log.IntegrationAdaptorsLogger('MHS_SYNC_ASYNC_WORKFLOW')

ASYNC_RESPONSE_EXPECTED = 'async_response_expected'
MESSAGE_DATA = 'data'
CORRELATION_ID = 'correlation_id'


class SyncAsyncWorkflow(common_synchronous.CommonSynchronousWorkflow):
    """Handles the workflow for the sync-async messaging pattern."""

    def __init__(self,
                 party_id: str,
                 transmission: ta.TransmissionAdaptor = None,
                 sync_async_store: pa.PersistenceAdaptor = None):
        """Create a new SyncAsyncWorkflow that uses the specified dependencies to load config, build a message and
        send it.
        :param transmission: The component that can be used to send messages.
        :param sync_async_store: The resynchronisor state store
        :param party_id: The party ID of this MHS. Sent in ebXML requests.
        """

        self.transmission = transmission
        self.sync_async_store = sync_async_store
        self.party_id = party_id

    async def handle_outbound_message(self, message_id: str, correlation_id: str, interaction_details: dict,
                                      payload: str) -> Tuple[int, str]:
        raise NotImplementedError()

    async def handle_inbound_message(self, message_id: str, correlation_id: str, work_description: wd.WorkDescription,
                                     payload: str):
        logger.info('001', 'Entered sync-async inbound workflow')
        await self._update_state_store(work_description, wd.MessageStatus.INBOUND_RESPONSE_RECEIVED)
        await self._add_to_sync_async_store(message_id, {CORRELATION_ID: correlation_id, MESSAGE_DATA: payload})
        logger.info('004', 'Placed message onto inbound queue successfully')
        await self._update_state_store(work_description, wd.MessageStatus.INBOUND_SYNC_ASYNC_MESSAGE_STORED)

    async def _update_state_store(self, work_description, status):
        retry = 0
        while retry < 3:  # TODO: Set to config value
            try:
                await work_description.set_status(status)
                logger.info('006', 'Updated work description store')
                return
            except Exception as e:
                logger.error('005', 'Exception raised whilst updating state store: {exception}', {'exception': e})
                if retry == 3:
                    raise e
                retry += 1
                await asyncio.sleep(0.5)  # TODO: Set to config value

    async def _add_to_sync_async_store(self, key, data):
        logger.info('002', 'Attempting to add inbound message to sync-async store')
        retry = 0
        while True:  # TODO set config
            try:
                await self.sync_async_store.add(key, data)
                logger.info('003', 'Successfully updated state store')
                break
            except Exception as e:
                logger.warning('021', 'Exception raised while adding to sync-async store {exception} {retry}',
                               {'exception': e, 'retry': retry})
                if retry == 3:  # TODO: config
                    logger.error('022', 'Final retry has been attempted for adding message to sync async store')
                    raise e
                retry += 1
                await asyncio.sleep(0.5)  # TODO config

    def prepare_message(self, interaction_details: dict, content: str, message_id: str) -> Tuple[bool, str]:
        """Prepare a message to be sent for the specified interaction. Wraps the provided content if required.

        :param interaction_details: The details of the interaction looked up from the config manager.
        :param content: The message content to be sent.
        :param message_id: message id to use in the message header.
        :return: A tuple containing:
        1. A flag indicating whether this message should be sent asynchronously
        2. The message to send
        """

        interaction_details[ebxml_envelope.MESSAGE_ID] = message_id

        is_async = interaction_details[ASYNC_RESPONSE_EXPECTED]
        if is_async:
            message = self._wrap_message_in_ebxml(interaction_details, content)
        else:
            message = content

        return is_async, message

    def send_message(self, interaction_details: dict, message: str) -> str:
        """Send the provided message for the interaction named. Returns the response received immediately, but note that
        if the interaction will result in an asynchronous response, this will simply be the acknowledgement of the
        request.

        :param interaction_details: The details of the interaction looked up from the config manager.
        :param message: A string representing the message to be sent.
        :return: A string containing the immediate response to the message sent.
        :raises: An UnknownInteractionError if the interaction_name specified was not found.
        """

        response = self.transmission.make_request(interaction_details, message)
        logger.info("0001", "Message sent to Spine, and response received.")
        return response

    def _wrap_message_in_ebxml(self, interaction_details: Dict[str, str], content: str) -> str:
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

        _, _, message = request.serialize()

        logger.info("0002", "Generated ebXML wrapper with {ConversationId}", {"ConversationId": conversation_id})
        return message
