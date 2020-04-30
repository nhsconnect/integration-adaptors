from fhir.resources.fhirreference import FHIRReference
from fhir.resources.patient import Patient


def get_ha_identifier(patient: Patient):
    return patient.managingOrganization.identifier.value


def get_gp_identifier(patient: Patient):
    gp = patient.generalPractitioner[0]  # type: FHIRReference
    return gp.identifier.value