"""Modules related to management of the workflow for supported messaging patterns."""
from typing import Dict

from comms import queue_adaptor

from mhs_common.state import persistence_adaptor
from mhs_common.transmission import transmission_adaptor
from mhs_common.workflow.asynchronous_express import AsynchronousExpressWorkflow
from mhs_common.workflow.asynchronous_reliable import AsynchronousReliableWorkflow
from mhs_common.workflow.common import CommonWorkflow
from mhs_common.workflow.intermediary_reliable import IntermediaryReliableWorkflow
from mhs_common.workflow.synchronous import SynchronousWorkflow
from mhs_common.workflow.sync_async import SyncAsyncWorkflow

ASYNC_EXPRESS = 'async-express'
ASYNC_RELIABLE = 'async-reliable'
FORWARD_RELIABLE = 'forward-reliable'
SYNC = 'sync'
SYNC_ASYNC = 'sync-async'


def get_workflow_map(party_key: str = None,
                     work_description_store: persistence_adaptor.PersistenceAdaptor = None,
                     sync_async_store: persistence_adaptor.PersistenceAdaptor = None,
                     transmission: transmission_adaptor.TransmissionAdaptor = None,
                     inbound_async_queue: queue_adaptor.QueueAdaptor = None,
                     sync_async_store_retries: int = None,
                     sync_async_store_retry_delay: int = None,
                     inbound_queue_max_retries: int = None,
                     inbound_queue_retry_delay: int = None
                     ) -> Dict[str, CommonWorkflow]:
    """
    Get a map of workflows. Keys for each workflow should correspond with keys used in interactions.json

    :return: a map of workflows
    """
    return {
        ASYNC_EXPRESS: AsynchronousExpressWorkflow(party_key, work_description_store, transmission,
                                                   inbound_async_queue, inbound_queue_max_retries, inbound_queue_retry_delay),
        ASYNC_RELIABLE: AsynchronousReliableWorkflow(),
        FORWARD_RELIABLE: IntermediaryReliableWorkflow(),
        SYNC_ASYNC: SyncAsyncWorkflow(party_key, transmission=transmission, sync_async_store=sync_async_store,
                                      sync_async_store_max_retries=sync_async_store_retries,
                                      sync_async_store_retry_delay=sync_async_store_retry_delay),
        SYNC: SynchronousWorkflow()
    }
