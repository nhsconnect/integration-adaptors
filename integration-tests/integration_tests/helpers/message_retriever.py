from __future__ import print_function

from proton.utils import BlockingConnection


def get_inbound_response():
    conn = BlockingConnection("localhost:5672")
    receiver = conn.create_receiver("inbound")
    msg = receiver.receive(timeout=30)
    receiver.accept()
    conn.close()

    return msg.properties['message-id'], msg.properties['correlation-id'], msg.body
