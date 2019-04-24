class Interchange(object):
    """
    The edifact interchange that is used to interface with NHAIS
    """

    def __init__(self, header):
        """
        :param header: The header of the interchange
        """
        self.header = header

    def to_edifact(self):
        edifact_interchange = f"AAA-{self.header}"
        return edifact_interchange
