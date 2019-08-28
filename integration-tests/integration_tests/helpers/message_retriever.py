from __future__ import print_function

from proton.utils import BlockingConnection

from integration_tests.helpers import methods


def get_inbound_response():
    """ Retrieve the response from the inbound queue

    :return: A tuple of the message-id, correlation-id and the message body.
    """
    connection = BlockingConnection(methods.get_mhs_inbound_queue())
    receiver = connection.create_receiver("inbound")
    message = receiver.receive(timeout=30)
    receiver.accept()
    connection.close()

    return message.properties['message-id'], message.properties['correlation-id'], message.body
