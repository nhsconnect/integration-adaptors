import utilities.integration_adaptors_logger as log
from comms import queue_adaptor
from retry import retriable_action
from utilities import timing, config

logger = log.IntegrationAdaptorsLogger(__name__)

class MeshOutboundWrapper:

    def __init__(self,
                 queue_adaptor: queue_adaptor.QueueAdaptor = None):
        self.queue_adaptor = queue_adaptor
        self.queue_max_retries = int(config.get_config('MAX_RETRIES', default='10'))
        self.queue_retry_delay = float(config.get_config('RETRY_DELAY', default='0.1'))
        self.transmission = None

    async def _publish_message_to_inbound_queue(self, message):

        result = await retriable_action.RetriableAction(
            lambda: self._put_message_onto_queue_with(message),
            self.queue_max_retries,
            self.queue_retry_delay) \
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





