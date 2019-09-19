from comms.common_https import CommonHttps
from utilities import integration_adaptors_logger as log

logger = log.IntegrationAdaptorsLogger('MSG_SENDER')


class MessageSender(object):
    
    def __init__(self, mhs_address):
        self.mhs_address = mhs_address
        
    async def send_message_to_mhs(self, interaction_id, message_body):
        logger.info('001', 'Preparing message headers to send to mhs address')
        headers = {
            'Interaction-Id': interaction_id,
            'sync-async': 'true'
        }

        response = await CommonHttps.make_request(url=self.mhs_address,
                                                  headers=headers,
                                                  body=message_body,
                                                  method='POST')
        logger.info('002', 'Response received from MHS')
        return response
