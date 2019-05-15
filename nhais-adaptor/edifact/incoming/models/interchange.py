from edifact.incoming.models.message import Messages


class InterchangeHeader:
    """
    A representation of the incoming edifact interchange header
    """

    def __init__(self, sender, recipient, date_time):
        """
        :param sender: the incoming senders cypher
        :param recipient: the recipient of the incoming interchange
        :param date_time: the date time stamp of the incoming interchange
        """
        self.sender = sender
        self.recipient = recipient
        self.date_time = date_time


class Interchange:
    """
    A representation of the incoming edifact interchange
    """

    def __init__(self, header: InterchangeHeader, messages: Messages):
        """
        :param header: the interchange header of the incoming interchange
        :param messages: a list of messages from the incoming interchange
        """
        self.header = header
        self.msgs = messages
