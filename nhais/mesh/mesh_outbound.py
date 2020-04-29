import utilities.integration_adaptors_logger as log
from comms import proton_queue_adaptor
from utilities import timing, config

logger = log.IntegrationAdaptorsLogger(__name__)


class MeshOutboundWrapper:

    def __init__(self):
        self.queue_adaptor = proton_queue_adaptor.ProtonQueueAdaptor(
            urls=config.get_config('OUTBOUND_QUEUE_BROKERS').split(','),
            queue=config.get_config('OUTBOUND_QUEUE_NAME'),
            username=config.get_config('OUTBOUND_QUEUE_USERNAME', default=None),
            password=config.get_config('OUTBOUND_QUEUE_PASSWORD', default=None),
            max_retries=int(config.get_config('OUTBOUND_QUEUE_MAX_RETRIES', default='3')),
            retry_delay=int(config.get_config('OUTBOUND_QUEUE_RETRY_DELAY', default='100')) / 1000)
        self.transmission = None

    async def _publish_message_to_outbound_queue(self, message):
        await self._put_message_onto_queue_with(message)

    async def _put_message_onto_queue_with(self, message):
        await self.queue_adaptor.send_async({'payload': message})

    @timing.time_function
    async def send(self, message):
        await self._publish_message_to_outbound_queue(message)
