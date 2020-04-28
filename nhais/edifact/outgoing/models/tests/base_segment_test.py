import abc
import unittest
from unittest import TestCase

import typing

from edifact.edifact_exception import EdifactValidationException
from edifact.outgoing.models.segment import Segment

class BaseSegmentTest(unittest.TestCase):

    @abc.abstractmethod
    def _create_segment(self):
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
    def _get_e
    
    def __test_missing_params(self, all_params: dict, constructor):
        for key, value in all_params.items():
            missing = dict(all_params)
            missing[key] = None
            with_missing = constructor(**missing)
            with self.assertRaises(EdifactValidationException, msg=f'missing "{key}" did not fail validation') as ctx:
                with_missing.to_edifact()
            test.assertEqual(f'{with_missing.key}: Attribute {key} is required', ctx.exception.args[0])
    
    
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

