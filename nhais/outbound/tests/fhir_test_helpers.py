from fhir.resources.fhirreference import FHIRReference
from fhir.resources.identifier import Identifier
from fhir.resources.patient import Patient

GP_ID = 'GP123'
HA_ID = 'HA456'
PATIENT_ID = '54321'

def create_org_ref(identifier_value: str):
    ref = FHIRReference()
    ref.type = "Organisation"
    identifier = Identifier()
    identifier.value = identifier_value
    ref.identifier = identifier
    return ref


def create_patient() -> Patient:
    patient = Patient()
    patient.id = PATIENT_ID
    patient.generalPractitioner = [create_org_ref(GP_ID)]
    patient.managingOrganization = create_org_ref(HA_ID)
    return patient