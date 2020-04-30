from proton import Message, Timeout
from proton.utils import BlockingConnection


class BlockingQueueAdaptor(object):
    """
    Allows blocking reads from an AMQP message queue
    """

    def __init__(self, username: str, password: str, queue_url: str, queue_name: str):
        self.username = username
        self.password = password
        self.queue_url = queue_url
        self.queue_name = queue_name

    def get_next_message_on_queue(self) -> Message:
        """
        Gets the next message from the queue
        :return: Message read from queue
        """
        connection = BlockingConnection(self.queue_url, user=self.username, password=self.password)
        receiver = connection.create_receiver(self.queue_name)
        message = receiver.receive(timeout=30)
        receiver.accept()
        connection.close()

        return message

    def drain(self):
        """
        Drain the queue to prevent test failures caused by previous failing tests not ack'ing all of their messages
        """
        connection = BlockingConnection(self.queue_url, user=self.username, password=self.password)
        receiver = connection.create_receiver(self.queue_name)
        try:
            while True:
                receiver.receive(timeout=1)
                receiver.accept()
        except Timeout:
            pass
        finally:
            connection.close()
