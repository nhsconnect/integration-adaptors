import os


def get_message_queue_host() -> str:
    return "http://" + os.environ.get('MESSAGE_QUEUE_ADDRESS', 'localhost:5672') + "/component-integration"
