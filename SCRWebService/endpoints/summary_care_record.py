"""The Summary Care Record endpoint"""
import json
from typing import Dict, Optional
import tornado.web
import tornado.ioloop
import utilities.integration_adaptors_logger as log
from utilities import message_utilities
from utilities import mdc

from message_handling import message_forwarder as mh
from builder.pystache_message_builder import MessageGenerationError
from message_handling.message_forwarder import MessageSendingError

logger = log.IntegrationAdaptorsLogger(__name__)


class SummaryCareRecord(tornado.web.RequestHandler):
    """ The SummaryCareRecord endpoint - provides the entrypoint for inbound
        ** Note: It is current expected behavior of the system that verification of the inputs is performed
        ** by the Pystache library as a part of the message generation
    """

    def initialize(self, forwarder: mh.MessageForwarder) -> None:
        """
        SummaryCareRecord endpoint class
        :param forwarder: A message forwarder, parsed messages are pushed to this object for processing
        :return:
        """
        self.forwarder = forwarder

    async def post(self):
        """
        Receives a json payload, parses the appropriate message details before processing the message contents
        :return:
        """

        scr_input_json = self._extract_message_body()
        interaction_name = self._extract_interaction_name()
        correlation_id = self._extract_correlation_id()
        message_id = self._extract_message_id()
        logger.info('Extracted message content, attempting to forward the message')
        response = await self._process_message(interaction_name, scr_input_json, message_id, correlation_id)
        self.write(json.dumps(response))

    async def _process_message(self, interaction_name: str,
                               scr_input_json: Dict,
                               message_id: Optional[str],
                               correlation_id: str):
        """
        Processes the outbound message by delegating to the forwarder
        :param interaction_name: Human readable name of the interaction
        :param scr_input_json: Dictionary of desired input data
        :param message_id
        :param correlation_id
        :return: Result of forwarding the message to the MHS
        """
        try:
            result = await self.forwarder.forward_message_to_mhs(interaction_name,
                                                                 scr_input_json,
                                                                 message_id,
                                                                 correlation_id
                                                                 )
            return result
        except MessageGenerationError as e:
            logger.exception('Failed to generate message')
            raise tornado.web.HTTPError(400, 'Error whilst generating message',
                                        reason=f'Error whilst generating message: {str(e)}')
        except MessageSendingError as e:
            logger.exception('Exception raised whilst attempting to send the message to the MHS')
            raise tornado.web.HTTPError(500, f'Error whilst attempting to send the message to the MHS: {str(e)}',
                                        reason=f'Error whilst attempting to send the message to the MHS: {str(e)}')

    def _extract_interaction_name(self) -> str:
        """
        Extracts the human readable interaction name from the message header
        :return: The value assigned to the `interaction-id` header key
        """
        interaction_name = self.request.headers.get('interaction-name')
        if not interaction_name:
            logger.error('No interaction-name header provided with inbound message')
            raise tornado.web.HTTPError(400, 'No interaction-id header provided',
                                        reason=f'No interaction-name header provided')
        return interaction_name

    def _extract_message_body(self):
        """Extracts the message body from the request
        :return: The message body
        """
        try:
            return json.loads(self.request.body)
        except json.decoder.JSONDecodeError as e:
            logger.exception('Exception raised whilst parsing message body.')
            raise tornado.web.HTTPError(400, 'Failed to parse json body from request',
                                        reason=f'Exception raised while parsing message body: {str(e)}')

    def _extract_correlation_id(self):
        """
        Attempts to extract the correlation-id from the message headers, if this fails a new one is generated,
        either way the correlation id is set in the logger
        :return: A UUID
        """
        correlation_id = self.request.headers.get('Correlation-Id', None)
        if not correlation_id:
            correlation_id = message_utilities.get_uuid()
            mdc.correlation_id.set(correlation_id)
            logger.info("No correlation-id header found in message, generated a new one")
        else:
            mdc.correlation_id.set(correlation_id)
            logger.info('Found correlation id on incoming request.')
        return correlation_id

    def _extract_message_id(self) -> Optional[str]:
        """
        Attempts to extract a message id from the headers, there is no consequence for not providing this as the
        SCR adaptor doesn't use message id, and the MHS will generate one
        :return:
        """
        message_id = self.request.headers.get('Message-Id', None)
        if message_id:
            mdc.message_id.set(message_id)
            logger.info("Found message id on incoming request")
        return message_id
