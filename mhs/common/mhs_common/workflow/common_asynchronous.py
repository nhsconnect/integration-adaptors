"""This module defines the common base for all asynchronous workflows."""

import mhs_common.workflow.common as common
import abc
from mhs_common.state import work_description as wd


class CommonAsynchronousWorkflow(common.CommonWorkflow):
    """Common functionality across all asynchronous workflows."""
    pass
