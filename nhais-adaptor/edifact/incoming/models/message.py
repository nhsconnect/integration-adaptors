from edifact.incoming.models.transaction import Transactions


class MessageSegmentBeginningDetails:
    """
    A representation of the incoming edifact message beginning details contained in a message
    """

    def __init__(self, reference_number):
        """
        :param reference_number: the reference number from the incoming edifact interchange
        will be used to determine if the transaction is approved
        """
        self.reference_number = reference_number


class MessageSegment:
    """
    A representation of the incoming edifact message
    """

    def __init__(self, message_beginning: MessageSegmentBeginningDetails, transactions: Transactions):
        """
        :param message_beginning: the incoming message beginning section
        :param transactions: the incoming message registration details
        """
        self.message_beginning = message_beginning
        self.transactions = transactions


class Messages(list):
    """
    A collection of all the incoming messages contained within an interchange
    """

    def __init__(self, messages):
        """
        :param messages: a collections of the incoming messages
        """
        self.messages = messages
        super().__init__(messages)
