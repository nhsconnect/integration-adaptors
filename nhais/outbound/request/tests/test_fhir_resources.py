import json
import os
import unittest

from fhir.resources.fhirabstractbase import FHIRValidationError
from fhir.resources.humanname import HumanName
from fhir.resources.identifier import Identifier
from fhir.resources.patient import Patient

root_dir = os.path.dirname(os.path.abspath(__file__))

valid_json_patient1 = root_dir + "/data/patient1.json"
with open(valid_json_patient1) as file:
    VALID_REQUEST_BODY1 = json.load(file)

valid_json_patient2 = root_dir + "/data/patient2.json"
with open(valid_json_patient2) as file:
    VALID_REQUEST_BODY2 = json.load(file)

invalid_json_patient_id = root_dir + "/data/patient_invalid_id.json"
with open(invalid_json_patient_id) as file:
    INVALID_ID_REQUEST_BODY = json.load(file)

invalid_json_patient_id = root_dir + "/data/patient_unknown_property.json"
with open(invalid_json_patient_id) as file:
    UNKNOWN_PROPERTY = json.load(file)


class TestFhirResource(unittest.TestCase):
    """
    Using Pipenv to install the "fhir.resources" package did not work, it tries to install the "fhir" package instead.
    As a workaround pip was used to install the package into the virtualenv directly:
    $ pipenv shell
    (nhais) $ pip install fhir.resources
    """

    def test_valid_patient1(self):
        p = Patient(VALID_REQUEST_BODY1)
        # verify that extensions are accessible
        self.assertEquals("Y12345", p.extension[0].valueReference.identifier.value)

    def test_valid_patient2(self):
        p = Patient(VALID_REQUEST_BODY2)
        # verify that extensions are accessible
        self.assertEquals("2", p.extension[0].extension[0].valueCodeableConcept.coding[0].code)

    def test_invalid_ID(self):
        expected = """Wrong type <class 'int'> for property "value" on <class 'fhir.resources.identifier.Identifier'>, expecting <class 'str'>"""
        try:
            p = Patient(INVALID_ID_REQUEST_BODY)
        except FHIRValidationError as e:
            # need to traverse the error tree to build the full path
            self.assertEqual('identifier.0', e.errors[0].path)
            self.assertEqual('value', e.errors[0].errors[0].path)
            # error message deep in tree and very specific to python classes and types
            path, message = self._parse_fhir_error(e)
            self.assertEquals(expected, e.errors[0].errors[0].errors[0].args[0])

    def _parse_fhir_error(self, e, path=''):
        if isinstance(e, FHIRValidationError):
            if e.path:
                if path:
                    path = f'{path}.{e.path}'
                else:
                    path = e.path
            if e.errors:
                # TODO: could be multiple errors
                return self._parse_fhir_error(e.errors[0], path)
        return path, e.args[0]


    def test_unknown_property(self):
        expected = 'Superfluous entry "invalidProperty" in data for <fhir.resources.humanname.HumanName object at 0x[0-9a-f]+>'
        try:
            p = Patient(UNKNOWN_PROPERTY)
        except FHIRValidationError as e:
            # path is to the parent object not the field causing the error
            self.assertEqual('name.0', e.errors[0].path)
            # the error itself contains info about the internal class structure and memory address
            self.assertRegex(e.errors[0].errors[0].args[0], expected)

    def test_output_json(self):
        p = Patient()
        p.name = [HumanName()]
        p.name[0].family = "Lastname"
        p.name[0].given = ["Firstname"]
        # no runtime errors if invalid fields are set (but IntelliJ IDE flags a warning)
        # this extra field does not appear in output JSON
        # need to be careful we don't lose data this way
        p.name[0].somethingelse = "asdf"
        p.identifier = [Identifier()]
        # p.identifier[0] = Identifier()
        p.identifier[0].value = "123"
        json_dict = p.as_json()
        json_str = json.dumps(json_dict)
        expected = '{"identifier": [{"value": "123"}], "name": [{"family": "Lastname", "given": ["Firstname"]}], "resourceType": "Patient"}'
        self.assertEqual(expected, json_str)
