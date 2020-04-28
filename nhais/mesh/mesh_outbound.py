import utilities.integration_adaptors_logger as log
from comms import proton_queue_adaptor
from retry import retriable_action
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

    async def _publish_message_to_inbound_queue(self, message):
        result = await retriable_action.RetriableAction(
            lambda: self._put_message_onto_queue_with(message),
            self.queue_adaptor.max_retries,
            self.queue_adaptor.retry_delay) \
            .execute()

        if not result.is_successful:
            logger.error("Exceeded the maximum number of retries, {max_retries} retries, when putting "
                         "message onto inbound queue",
                         fparams={"max_retries": self.queue_max_retries})


    async def _put_message_onto_queue_with(self, message):
        await self.queue_adaptor.send_async({'payload': message})

    @timing.time_function
    async def send(self, message):
        await self._publish_message_to_inbound_queue(message)





