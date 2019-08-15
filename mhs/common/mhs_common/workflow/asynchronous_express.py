"""This module defines the asynchronous express workflow."""
from typing import Tuple

import utilities.integration_adaptors_logger as log
from comms import transmission_adaptor

from mhs_common.state import persistence_adaptor, work_description
from mhs_common.workflow import common_asynchronous

logger = log.IntegrationAdaptorsLogger('ASYNC_EXPRESS_WORKFLOW')


class AsynchronousExpressWorkflow(common_asynchronous.CommonAsynchronousWorkflow):
    """Handles the workflow for the asynchronous express messaging pattern."""

    def __init__(self, persistence_store: persistence_adaptor.PersistenceAdaptor,
                 transmission: transmission_adaptor.TransmissionAdaptor, party_key: str):
        self.persistence_store = persistence_store
        self.transmission = transmission
        self.party_key = party_key

    async def handle_outbound_message(self, message_id: str, correlation_id: str, interaction_details: dict,
                                      payload: str) -> Tuple[int, str]:
        logger.info('0001', 'Entered async express workflow to handle outbound message')
