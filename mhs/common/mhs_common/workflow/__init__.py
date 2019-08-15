"""Modules related to management of the workflow for supported messaging patterns."""
from typing import Dict

from comms import transmission_adaptor

from mhs_common.state import persistence_adaptor
from mhs_common.workflow.asynchronous_express import AsynchronousExpressWorkflow
from mhs_common.workflow.asynchronous_reliable import AsynchronousReliableWorkflow
from mhs_common.workflow.common import CommonWorkflow
from mhs_common.workflow.intermediary_reliable import IntermediaryReliableWorkflow
from mhs_common.workflow.synchronous import SynchronousWorkflow


def get_workflow_map(persistence_store: persistence_adaptor.PersistenceAdaptor,
                     transmission: transmission_adaptor.TransmissionAdaptor,
                     party_key: str) -> Dict[str, CommonWorkflow]:
    """
    Get a map of workflows. Keys for each workflow should correspond with keys used in interactions.json

    :return: a map of workflows
    """
    return {
        'async-express': AsynchronousExpressWorkflow(persistence_store, transmission, party_key),
        'async-reliable': AsynchronousReliableWorkflow(),
        'forward-reliable': IntermediaryReliableWorkflow(),
        'sync': SynchronousWorkflow(),
    }
