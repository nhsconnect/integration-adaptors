from sequence.key_generator import SequenceKeyGenerator


class InterchangeIdGenerator(object):

    def __init__(self):
        self.key_generator = SequenceKeyGenerator()

    def next_interchange_id(self):
        return 1