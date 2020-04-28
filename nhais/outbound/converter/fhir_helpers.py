from fhir.resources.patient import Patient


def get_ha_identifier(patient: Patient):
    return patient.managingOrganization.identifier.value
