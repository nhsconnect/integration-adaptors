from typing import Any, Dict

import tornado.web
import utilities.message_utilities as message_utilities
import utilities.integration_adaptors_logger as log
from comms.http_headers import HttpHeaders

from mhs_common import workflow
from mhs_common.configuration import configuration_manager

logger = log.IntegrationAdaptorsLogger(__name__)


class BaseHandler(tornado.web.RequestHandler):
    """A base Tornado request handler with common functionality used by handlers in MHS outbound and MHS inbound."""

    def initialize(self, workflows: Dict[str, workflow.CommonWorkflow],
                   config_manager: configuration_manager.ConfigurationManager):
        """Initialise this request handler with the provided dependencies.

        :param workflows: The workflows to use to send messages.
        :param config_manager: The object that can be used to obtain configuration details.
        """
        self.workflows = workflows
        self.config_manager = config_manager

    def write_error(self, status_code: int, **kwargs: Any):
        reason = self._reason  # Don't inline this, as self.set_status changes self._reason
        self.set_status(status_code)
        self.set_header(HttpHeaders.CONTENT_TYPE, 'text/plain')
        self.set_header(HttpHeaders.CORRELATION_ID, self._extract_correlation())
        self.finish(f'{status_code}: {reason}')

    def _extract_default_workflow(self, interaction_details, interaction_id):
        try:
            wf = self.workflows[interaction_details['workflow']]
        except KeyError as e:
            logger.error("Wasn't able to determine workflow for {InteractionId} . This likely is due to a "
                         "misconfiguration in interactions.json",
                         fparams={"InteractionId": interaction_id})
            raise tornado.web.HTTPError(500,
                                        f"Couldn't determine workflow to invoke for interaction ID: {interaction_id}",
                                        reason=f"Couldn't determine workflow to invoke for interaction ID: "
                                        f"{interaction_id}") from e
        return wf

    def _get_interaction_details(self, interaction_id):
        interaction_details = self.config_manager.get_interaction_details(interaction_id)

        if interaction_details is None:
            logger.error('Unknown {InteractionId} in request', fparams={'InteractionId': interaction_id})
            raise tornado.web.HTTPError(404, f'Unknown interaction ID: {interaction_id}',
                                        reason=f'Unknown interaction ID: {interaction_id}')

        return interaction_details

    def _extract_correlation(self):
        correlation_id = self.request.headers.get(HttpHeaders.CORRELATION_ID, None)
        if correlation_id is None:
            return message_utilities.get_uuid()
        return correlation_id
