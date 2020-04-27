import abc


class Segment(object):
    """
    A segment is the basic building block of an edifact message.
    It represent each line in the edifact message that will be generated.
    example: NAD+GP+4826940,281:900'
    """

    TERMINATOR = "'"

    @property
    @abc.abstractmethod
    def key(self):
        """
        :return: the key of the segment for example NAD, DTM ...
        """
        raise NotImplementedError()

    @property
    @abc.abstractmethod
    def value(self):
        """
        :return: the value of the segment
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def pre_validate(self):
        """
        Validates non-stateful data items of the segment (excludes things like sequence numbers)
        :raises: EdifactValidationException
        """
        raise NotImplementedError()

    def _validate_stateful(self):
        """
        Validates stateful data items of the segment like sequence numbers
        :raises: EdifactValidationException
        """
        pass

    def validate(self):
        """
        Validates the entire segment including statement items like sequence numbers
        :raises: EdifactValidationException
        """
        self.pre_validate()

    def to_edifact(self):
        """
        generates the edifact message of the segment
        :return: a string of the formatted edifact message using the key and value
        """
        self.validate()
        edifact_segment = f"{self.key}+{self.value}{Segment.TERMINATOR}"
        return edifact_segment


class ConstantSegment(Segment):
    """
    A general segment implementation for segments that always have a constant value and don't require parameters
    or validation
    takes in specific values required to generate a message trailer
    example: BGM+++507'
    """

    def __init__(self, key, value):
        self.__key = key
        self.__value = value

    @property
    def key(self):
        return self.__key

    @property
    def value(self):
        return self.__value

    def pre_validate(self):
        pass


class SegmentCollection(list):
    """
    A collection of segments base class
    """

    def __init__(self, segments):
        """
        :param segments: the collection of segments
        """
        self.segments = segments
        super().__init__(segments)

    def to_edifact(self):
        """
        Generated the edifact message of the collection
        :return: an edifact string representation of the Segment collection
        """
        edifact_message = ''.join([segment.to_edifact() for segment in self.segments])
        return edifact_message

    def add_segments(self, segments):
        self.segments.extend(segments)
