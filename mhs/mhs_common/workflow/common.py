"""This module defines the mhs_common base of all workflows."""


class UnknownInteractionError(Exception):
    """Raised when an unknown interaction has been specified"""

    def __init__(self, interaction_name):
        """Create a new UnknownInteractionError for the specified interaction name.

        :param interaction_name: The interaction name requested but not found.
        """
        self.interaction_name = interaction_name


class CommonWorkflow:
    """Common functionality across all workflows."""
    pass
