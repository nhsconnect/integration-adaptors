"""
Provides tests around the Asynchronous Express workflow, including sync-async wrapping
"""
import json
from unittest import TestCase

from comms.blocking_queue_adaptor import BlockingQueueAdaptor
from utilities import config


class NhaisIntegrationTests(TestCase):
    """
     These tests demonstrate each outbound (GP -> HA) transaction without HA replies
    """

    def __init__(self):
        super().__init__()
        # TODO: how to we specify the queue name?!?
        self.mq_wrapper = BlockingQueueAdaptor(username=config.get_config('OUTBOUND_QUEUE_USERNAME', default=None),
                   password=config.get_config('OUTBOUND_QUEUE_PASSWORD', default=None),
                   queue_url=config.get_config('OUTBOUND_QUEUE_HOST'),
                   queue_name='mesh_outbound')


    def setUp(self):
        self.mq_wrapper.drain()

    def test_acceptance_transaction(self):
        pass


