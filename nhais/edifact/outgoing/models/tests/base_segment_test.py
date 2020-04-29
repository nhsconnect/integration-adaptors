import abc

from edifact.edifact_exception import EdifactValidationException
from edifact.outgoing.models.segment import Segment


class BaseSegmentTest(abc.ABC):
    """
    A base test for subclasses of Segment. Implementor must also inherit unittest.TestCase.
    """

    @abc.abstractmethod
    def _create_segment(self) -> Segment:
        """
        :return: a valid Segment with all attributes populated
        """
        pass

    @abc.abstractmethod
    def _get_attributes(self):
        """
        :return: all of the Segments settable attributes
        """
        pass
    
    @abc.abstractmethod
    def _get_expected_edifact(self):
        """
        :return: the expected EDIFACT for the segment returned by _create_segment()
        """
        pass

    def test_to_edifact(self):
        segment = self._create_segment()
        edifact = segment.to_edifact()
        self.assertEqual(self._get_expected_edifact(), edifact)

    def test_missing_attributes(self):
        self.__test_missing_properties(self._get_attributes(), self._create_segment)

    def __test_missing_properties(self, attribute_names: list, generator):
        """
        :param test: instance of the test case
        :param attribute_names: names of all required attributes in the Segment
        :param generator: a no-arg function that generates an instance of the Segment
        :return:
        """
        for attr_name in attribute_names:
            instance = generator()
            setattr(instance, attr_name, None)
            with self.assertRaises(EdifactValidationException, msg=f'missing "{attr_name}" did not fail validation') as ctx:
                instance.to_edifact()
            self.assertEqual(f'{instance.key}: Attribute {attr_name} is required', ctx.exception.args[0])

