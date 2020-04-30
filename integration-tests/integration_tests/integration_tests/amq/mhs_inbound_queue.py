import os

from comms.blocking_queue_adaptor import BlockingQueueAdaptor

MHS_INBOUND_QUEUE = BlockingQueueAdaptor(os.environ.get('MHS_SECRET_INBOUND_QUEUE_USERNAME', None),
                                         os.environ.get('MHS_SECRET_INBOUND_QUEUE_PASSWORD', None),
                                         os.environ.get('MHS_INBOUND_QUEUE_BROKERS', 'amqp://localhost:5672'),
                                         os.environ.get('MHS_INBOUND_QUEUE_NAME', 'inbound'))
