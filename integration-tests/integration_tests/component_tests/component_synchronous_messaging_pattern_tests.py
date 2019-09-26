"""
Provides tests around the Synchronous workflow
"""
from unittest import TestCase


class SynchronousMessagingPatternTests(TestCase):
    """
     These tests show a synchronous response from Spine via the MHS for the example message interaction of PDS
    (Personal Demographics Service).

    They make use of the fake-spine service, which has known responses for certain message ids.
    They make use of the fake-spine-route-lookup service, which has known responses for certain interaction ids.
    """

    def test_example(self):
        # Arrange
        # Act
        # Assert
        self.assertEqual(True, True, "Running example test for component test setup")

