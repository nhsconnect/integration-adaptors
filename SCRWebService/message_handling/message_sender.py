"""Module related to sending messages from the SCR Adaptor to the MHS"""
from typing import Optional

from comms.common_https import CommonHttps
from utilities import integration_adaptors_logger as log

logger = log.IntegrationAdaptorsLogger('MSG_SENDER')


class MessageSender(object):
    """Facilitates sending messages to from the SCR Adaptor to the MHS with the appropriate headers"""
    
    def __init__(self, mhs_address):
        self.mhs_address = mhs_address
        
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
        logger.info('001', 'Preparing message headers to send to mhs address')
        headers = self._build_headers(interaction_id, message_id, correlation_id)
        response = await CommonHttps.make_request(url=self.mhs_address,
                                                  headers=headers,
                                                  body=message_body,
                                                  method='POST')

        logger.info('002', 'Response received from MHS')
        return response

    def _build_headers(self, interaction_id: str, message_id: Optional[str], correlation_id: Optional[str]):
        headers = {
            'Interaction-Id': interaction_id,
            'sync-async': 'true'
        }
        if message_id:
            headers['message-id'] = message_id

        if correlation_id:
            headers['correlation-id'] = correlation_id

        return headers
