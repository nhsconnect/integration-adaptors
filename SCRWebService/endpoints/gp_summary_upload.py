import json
import tornado.web
import tornado.ioloop
import scr.gp_summary_update as scr_update
import utilities.integration_adaptors_logger as log
from message_handling import message_forwarder as mh
from builder.pystache_message_builder import MessageGenerationError

logger = log.IntegrationAdaptorsLogger('GP_SUM_UP')


class SummaryCareRecord(tornado.web.RequestHandler):

    def initialize(self, handler: mh.MessageForwarder) -> None:
        self.handler = handler

    def post(self):
        """
        Receives a json payload and attempts to populate a gp summary upload message, for testing purposes
        this end point currently returns the data provided
        :return:
        """

        logger.info('001', 'Message received for gp summary upl')
        scr_input_json = self._extract_message_body()
        interaction_name = self._extract_interaction_name()
        logger.info('002', 'Extracted message content, attempting to forward the message')
        response = self._process_message(interaction_name, scr_input_json)
        self.write(response)

    def _process_message(self, interaction_name, scr_input_json):
        try:
            result = self.handler.forward_message_to_mhs(interaction_name, scr_input_json)
            return result
        except MessageGenerationError as e:
            logger.error('003', 'Failed to generate message {exception}', {'exception': e})
            raise tornado.web.HTTPError(400, 'Error whilst generating message',
                                        reason=f'Error whilst generating message: {str(e)}')

    def _extract_interaction_name(self):
        interaction_id = self.request.headers.get('interaction-id')
        if not interaction_id:
            logger.error('0011', 'No interaction-id header provided with inbound message')
            raise tornado.web.HTTPError(400, 'No interaction-id header provided',
                                        reason=f'No interaction-id header provided')
        return interaction_id

    def _extract_message_body(self):
        try:
            return json.loads(self.request.body)
        except json.decoder.JSONDecodeError as e:
            logger.error('001', f'Failed to parse message body: {e}')
            raise tornado.web.HTTPError(400, 'Failed to parse json body from request',
                                        reason=f'Failed to parse json body from request: {str(e)}')
