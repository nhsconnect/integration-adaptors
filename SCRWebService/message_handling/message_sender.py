"""Module related to sending messages from the SCR Adaptor to the MHS"""
import json
from typing import Optional

from comms.common_https import CommonHttps
from utilities import integration_adaptors_logger as log

logger = log.IntegrationAdaptorsLogger(__name__)


class MessageSender(object):
    """Facilitates sending messages to from the SCR Adaptor to the MHS with the appropriate headers"""

    def __init__(self, mhs_address: str, ca_certs: str = None):
        """Initialise a new MessageSender instance.

        :param mhs_address: The MHS URL to send requests to.
        :param ca_certs: An optional string containing the path of the certificate authority certificate file to use
        when validating the MHS' certificates.
        """
        self.mhs_address = mhs_address
        self.ca_certs = ca_certs

    async def send_message_to_mhs(self, interaction_id: str,
                                  message_body: str,
                                  message_id: Optional[str],
                                  correlation_id: Optional[str]):
        """
        Sends a provided message body to the mhs for the given interaction_id
        :param interaction_id:
        :param message_body:
        :param message_id:
        :param correlation_id
        :return:
        """
        logger.info('Preparing message headers to send to mhs address')
        headers = self._build_headers(interaction_id, message_id, correlation_id)

        response = await CommonHttps.make_request(url=self.mhs_address,
                                                  headers=headers,
                                                  body=json.dumps({'payload': message_body}),
                                                  method='POST',
                                                  ca_certs=self.ca_certs)
        return response.body

    def _build_headers(self, interaction_id: str, message_id: Optional[str], correlation_id: Optional[str]):
        """
        Builds the appropriate header dictionary for the given parameters
        :param interaction_id:
        :param message_id:
        :param correlation_id:
        :return:
        """
        headers = {
            'Content-Type': 'application/json',
            'Interaction-Id': interaction_id,
            'wait-for-response': 'true'
        }
        if message_id:
            headers['message-id'] = message_id

        headers['correlation-id'] = correlation_id

        return headers
