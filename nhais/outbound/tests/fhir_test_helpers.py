from fhir.resources.fhirreference import FHIRReference
from fhir.resources.identifier import Identifier
from fhir.resources.patient import Patient


def create_org_ref(identifier_value: str):
    ref = FHIRReference()
    ref.type = "Organisation"
    identifier = Identifier()
    identifier.value = identifier_value
    ref.identifier = identifier
    return ref


def create_patient() -> Patient:
    patient = Patient()
    patient.id = '123'
    patient.generalPractitioner = [create_org_ref('GP123')]
    patient.managingOrganization = create_org_ref('HA456')
    return patient