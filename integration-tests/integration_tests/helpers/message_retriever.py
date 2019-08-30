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


def get_message_state(message_id):
    """ Retrieve the message state from the statedb

    :param message_id:
    :return: the message state
    """
    # store = dynamo_persistence_adaptor.DynamoPersistenceAdaptor(table_name=config.get_config('STATE_TABLE_NAME'))
    # store.get(message_id)
