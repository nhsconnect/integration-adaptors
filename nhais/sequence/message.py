from sequence.key_generator import SequenceKeyGenerator


class MessageIdGenerator(object):

    def __init__(self):
        self.key_generator = SequenceKeyGenerator()

    def next_message_id(self):
        return 1