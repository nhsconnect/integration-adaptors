from fhir.resources.identifier import Identifier
from fhir.resources.organization import Organization
from fhir.resources.patient import Patient


def get_ha_identifier(patient: Patient):
    ha = patient.managingOrganization[0]  # type: Organization
    ha_identifier = ha.identifier[0]  # type: Identifier
    return ha_identifier.value