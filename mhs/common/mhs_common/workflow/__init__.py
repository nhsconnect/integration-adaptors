"""Modules related to management of the workflow for supported messaging patterns."""
from typing import Dict

from comms import queue_adaptor

from mhs_common.routing import routing_reliability
from mhs_common.state import persistence_adaptor
from mhs_common.transmission import transmission_adaptor
from mhs_common.workflow.asynchronous_express import AsynchronousExpressWorkflow
from mhs_common.workflow.asynchronous_reliable import AsynchronousReliableWorkflow
from mhs_common.workflow.common import CommonWorkflow
from mhs_common.workflow.asynchronous_forward_reliable import AsynchronousForwardReliableWorkflow
from mhs_common.workflow.sync_async import SyncAsyncWorkflow
from mhs_common.workflow.sync_async_resynchroniser import SyncAsyncResynchroniser
from mhs_common.workflow.synchronous import SynchronousWorkflow

ASYNC_EXPRESS = 'async-express'
ASYNC_RELIABLE = 'async-reliable'
FORWARD_RELIABLE = 'forward-reliable'
SYNC = 'sync'
SYNC_ASYNC = 'sync-async'
RAW_QUEUE = 'raw-queue'


def get_workflow_map(party_key: str = None,
                     work_description_store: persistence_adaptor.PersistenceAdaptor = None,
                     sync_async_store: persistence_adaptor.PersistenceAdaptor = None,
                     transmission: transmission_adaptor.TransmissionAdaptor = None,
                     raw_queue_adaptor: queue_adaptor.QueueAdaptor = None,
                     inbound_async_queue: queue_adaptor.QueueAdaptor = None,
                     persistence_store_max_retries: int = None,
                     sync_async_store_retry_delay: int = None,
                     inbound_queue_max_retries: int = None,
                     inbound_queue_retry_delay: int = None,
                     max_request_size: int = None,
                     resynchroniser: SyncAsyncResynchroniser = None,
                     routing: routing_reliability.RoutingAndReliability = None
                     ) -> Dict[str, CommonWorkflow]:
    """
    Get a map of workflows. Keys for each workflow should correspond with keys used in interactions.json

    :return: a map of workflows
    """
    return {
        RAW_QUEUE: raw_queue_adaptor,
        ASYNC_EXPRESS: AsynchronousExpressWorkflow(party_key, work_description_store, transmission,
                                                   inbound_async_queue, inbound_queue_max_retries,
                                                   inbound_queue_retry_delay,
                                                   max_request_size,
                                                   persistence_store_max_retries=persistence_store_max_retries,
                                                   routing=routing),
        ASYNC_RELIABLE: AsynchronousReliableWorkflow(party_key, work_description_store, transmission,
                                                     inbound_async_queue, inbound_queue_max_retries,
                                                     inbound_queue_retry_delay, max_request_size,
                                                     persistence_store_max_retries=persistence_store_max_retries,
                                                     routing=routing),
        FORWARD_RELIABLE: AsynchronousForwardReliableWorkflow(party_key, work_description_store, transmission,
                                                              inbound_async_queue, inbound_queue_max_retries,
                                                              inbound_queue_retry_delay, max_request_size,
                                                              persistence_store_max_retries=persistence_store_max_retries,
                                                              routing=routing),

        SYNC_ASYNC: SyncAsyncWorkflow(sync_async_store=sync_async_store,
                                      sync_async_store_retry_delay=sync_async_store_retry_delay,
                                      resynchroniser=resynchroniser,
                                      work_description_store=work_description_store,
                                      persistence_store_max_retries=persistence_store_max_retries,
                                      ),
        SYNC: SynchronousWorkflow(party_key=party_key,
                                  work_description_store=work_description_store,
                                  transmission=transmission,
                                  max_request_size=max_request_size,
                                  persistence_store_max_retries=persistence_store_max_retries,
                                  routing=routing
                                  )
    }
