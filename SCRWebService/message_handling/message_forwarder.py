from typing import Any

from scr import gp_summary_update
from utilities import integration_adaptors_logger as log
from builder.pystache_message_builder import MessageGenerationError

GP_SUMMARY_UPLOAD_ID = 'REPC_IN150016UK05'

logger = log.IntegrationAdaptorsLogger('MSG-HANDLER')


class MessageSendingError(Exception):
    pass


class MessageForwarder(object):

    def __init__(self, interactions: dict):
        self.interactions = interactions

    def forward_message_to_mhs(self, interaction_name, message_contents: str):
        templater = self.interactions.get(interaction_name)
        populated_message = self._populate_message_template(templater, message_contents)

    def _get_interaction_templater(self, interaction_name):
        interaction_templater = self.interactions.get(interaction_name)
        if not interaction_templater:
            logger.error('002', 'Failed to find interaction templater for interaction name: {name}', 
                         {'name': interaction_name})
            raise MessageGenerationError(f'Failed to find interaction with interaction name: {interaction_name}')
        return interaction_templater
    
    def _populate_message_template(self, templater, supplier_message_parameters: str) -> str:
        try:
            return templater.populate_template_with_json_string(supplier_message_parameters)
        except Exception as e:
            logger.error('001', 'Message generation failed {exception}', {'exception': e})
            raise MessageGenerationError(str(e))

    def _send_message_to_mhs(self, message) -> Any:
        pass
