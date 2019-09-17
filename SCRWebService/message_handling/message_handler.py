from typing import Any

from scr import gp_summary_update
from utilities import integration_adaptors_logger as log

GP_SUMMARY_UPLOAD_ID = 'REPC_IN150016UK05'

logger = log.IntegrationAdaptorsLogger('MSG-HANDLER')


class MessageGenerationError(Exception):
    pass


class MessageSendingError(Exception):
    pass


class MessageHandler(object):

    def __init__(self):
        self.message_generator = gp_summary_update.SummaryCareRecord()

    def forward_message_to_mhs(self, message_contents: dict):
        populated_message = self._populate_message_template(message_contents)

    def _populate_message_template(self, supplier_message_parameters: dict) -> str:
        try:
            return self.message_generator.populate_template_with_json_string(supplier_message_parameters)
        except Exception as e:
            logger.error('001', 'Message generation failed {exception}', {'exception': e})
            raise MessageGenerationError(str(e))

    def _send_message_to_mhs(self, message) -> Any:
        return 0
