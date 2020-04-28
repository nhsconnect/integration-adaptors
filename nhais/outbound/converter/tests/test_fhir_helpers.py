import unittest

from fhir.resources.fhirreference import FHIRReference
from fhir.resources.identifier import Identifier
from fhir.resources.patient import Patient

from outbound.converter.fhir_helpers import get_ha_identifier


class TestFhirHelpers(unittest.TestCase):

    def test_get_ha_identifier(self):
        patient = Patient()
        org = FHIRReference()
        id = Identifier()
        id.value = 'IDVALUE'
        org.identifier = id
        patient.managingOrganization = org

        ha_identifier = get_ha_identifier(patient)

        self.assertEquals('IDVALUE', ha_identifier)