import re
import uuid
from typing import Union

from tornado.httputil import HTTPServerRequest

from fake_spine.spine_responses import SpineResponseBuilder, InboundRequest, OutboundResponse
from fake_spine.vnp_spine_message_builder import VnpMessageBuilder
from fake_spine import fake_spine_configuration
from utilities import integration_adaptors_logger as log

logger = log.IntegrationAdaptorsLogger(__name__)


class VnpSpineResponseException(Exception):
    pass


class VnpSpineResponseBuilder(SpineResponseBuilder):

    root_id_expression = re.compile('<id root="(?P<messageId>.+)"\\s*/>')
    conversation_id_expression = re.compile('<eb:ConversationId>(?P<conversationId>.+)</eb:ConversationId>')

    def __init__(self):
        super().__init__()
        self.inbound_request_headers = {}
        self.config = fake_spine_configuration.FakeSpineConfiguration()

    def _extract_message_id(self, request: HTTPServerRequest):
        body = request.body.decode()
        matches = self.root_id_expression.search(body)
        if matches:
            return matches.group('messageId')
        raise VnpSpineResponseException(f'Unable to find a MessageId in the request')

    def _extract_conversation_id(self, request: HTTPServerRequest):
        body = request.body.decode()
        matches = self.conversation_id_expression.search(body)
        if matches:
            return matches.group('conversationId')
        logger.info(f'Unable to find a ConversationId in the request')
        return ''

    def override_inbound_request_headers(self, inbound_request_headers):
        self.inbound_request_headers = inbound_request_headers
        return self

    def _build_from_message(self, outbound_request, file_location):
        message_builder = VnpMessageBuilder(file_location)
        message_id = self._extract_message_id(outbound_request)
        conversation_id = self._extract_conversation_id(outbound_request)
        template_parameters = {
            'message_id': str(uuid.uuid4()),
            'to_party_id': self.config.MHS_SECRET_PARTY_KEY,
            'ref_to_message_id': message_id,
            'conversation_id': conversation_id
        }
        return message_builder.build_message(template_parameters)

    def get_outbound_response(self, outbound_request: HTTPServerRequest) -> OutboundResponse:
        if self.response_file_location:
            response_body = self._build_from_message(outbound_request, self.response_file_location)
        else:
            response_body = ''  # some spine responses are empty
        return OutboundResponse(self.response_code, response_body)

    def get_inbound_request(self, outbound_request) -> Union[InboundRequest, None]:
        if self.inbound_request_file_location:
            inbound_request_body = self._build_from_message(outbound_request, self.inbound_request_file_location)
            return InboundRequest(inbound_request_body, self.inbound_request_headers)
        return None
