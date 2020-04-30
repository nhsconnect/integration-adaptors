import abc

from edifact.edifact_exception import EdifactValidationException


class Segment(abc.ABC):
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
        pass

    @property
    @abc.abstractmethod
    def value(self):
        """
        :return: the value of the segment
        """
        pass

    @abc.abstractmethod
    def pre_validate(self):
        """
        Validates non-stateful data items of the segment (excludes things like sequence numbers)
        :raises: EdifactValidationException
        """
        pass

    def _validate_stateful(self):
        """
        Validates stateful data items of the segment like sequence numbers
        :raises: EdifactValidationException
        """
        pass

    def validate(self):
        """
        Validates the entire segment including stateful items like sequence numbers
        :raises: EdifactValidationException
        """
        self.pre_validate()
        self._validate_stateful()

    def to_edifact(self):
        """
        generates the edifact message of the segment
        :return: a string of the formatted edifact message using the key and value
        """
        self.validate()
        edifact_segment = f"{self.key}+{self.value}{Segment.TERMINATOR}"
        return edifact_segment

    def _required(self, attribute_name):
        """
        A validation method to require that a specific property is truthy
        :param attribute_name: the attribute name to test
        :raises: EdifactValidationException if the attribute is not set
        """
        if not getattr(self, attribute_name, None):
            raise EdifactValidationException(f'{self.key}: Attribute {attribute_name} is required')