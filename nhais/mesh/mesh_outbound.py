import utilities.integration_adaptors_logger as log
from comms import queue_adaptor
from retry import retriable_action

from utilities import timing

logger = log.IntegrationAdaptorsLogger(__name__)

class MeshOutboundWrapper:

    def __init__(self,
                 queue_adaptor: queue_adaptor.QueueAdaptor = None):
        self.queue_adaptor = queue_adaptor
        self.queue_max_retries = 10
        self.queue_retry_delay = 0.1
        self.transmission = None

    async def _publish_message_to_inbound_queue(self,
                                                message_id: str,
                                                correlation_id: str,
                                                payload: str):

        result = await retriable_action.RetriableAction(
            lambda: self._put_message_onto_queue_with(message_id, correlation_id, payload),
            self.queue_max_retries,
            self.queue_retry_delay) \
            .execute()

        if not result.is_successful:
            logger.error("Exceeded the maximum number of retries, {max_retries} retries, when putting "
                         "message onto inbound queue",
                         fparams={"max_retries": self.inbound_queue_max_retries})


    async def _put_message_onto_queue_with(self, message_id, correlation_id, payload, attachments=None):
        await self.queue_adaptor.send_async({'payload': payload},
                                            properties={'message-id': message_id,
                                                        'correlation-id': correlation_id})

    @timing.time_function
    async def send(self, message):
        # TODO: publish message to queue
        await self._publish_message_to_inbound_queue("d6edbd6b-129a-4af1-9572-766f9292252f", "6ce48919-df48-4950-8397-ba144075f56d", "testpayload")
        pass




