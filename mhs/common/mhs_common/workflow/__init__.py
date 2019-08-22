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

ASYNC_EXPRESS = 'async-express'
ASYNC_RELIABLE = 'async-reliable'
FORWARD_RELIABLE = 'forward-reliable'
SYNC = 'sync'


def get_workflow_map(party_key: str = None, persistence_store: persistence_adaptor.PersistenceAdaptor = None,
                     transmission: transmission_adaptor.TransmissionAdaptor = None,
                     queue_adaptor: queue_adaptor.QueueAdaptor = None) -> Dict[str, CommonWorkflow]:
    """
    Get a map of workflows. Keys for each workflow should correspond with keys used in interactions.json

    :return: a map of workflows
    """
    return {
        ASYNC_EXPRESS: AsynchronousExpressWorkflow(party_key, persistence_store, transmission, queue_adaptor),
        ASYNC_RELIABLE: AsynchronousReliableWorkflow(),
        FORWARD_RELIABLE: IntermediaryReliableWorkflow(),
        SYNC: SynchronousWorkflow()
    }
