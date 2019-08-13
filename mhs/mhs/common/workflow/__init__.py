"""Modules related to management of the workflow for supported messaging patterns."""
from typing import Dict

from mhs.common.workflow.asynchronous_express import AsynchronousExpressWorkflow
from mhs.common.workflow.asynchronous_reliable import AsynchronousReliableWorkflow
from mhs.common.workflow.common import CommonWorkflow
from mhs.common.workflow.intermediary_reliable import IntermediaryReliableWorkflow
from mhs.common.workflow.synchronous import SynchronousWorkflow


def get_workflow_map() -> Dict[str, CommonWorkflow]:
    """
    Get a map of workflows. Keys for each workflow should correspond with keys used in interactions.json

    :return: a map of workflows
    """
    return {
        'async-express': AsynchronousExpressWorkflow(),
        'async-reliable': AsynchronousReliableWorkflow(),
        'forward-reliable': IntermediaryReliableWorkflow(),
        'sync': SynchronousWorkflow(),
    }
