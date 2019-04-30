from adaptor.outgoing.fhir_helpers.operation_definition import OperationDefinitionHelper as odh


def create_simple_patient():
    """
    creates a simple fhir patient with no previous names or addresses
    :return: Patient
    """
    patient = odh.create_patient_resource(resource_id="patient-1", nhs_number="NHSNO11111",
                                          title="Mr", first_name="Peter", last_name="Parker",
                                          gender="male", date_of_birth="2019-04-20",
                                          place_of_birth="Spidey Town",
                                          address_line_1="1 Spidey Way", city="Spidey Town", postcode="SP1 1AA")
    return patient


def create_simple_practitioner():
    """
    create a simple fhir practitioner
    :return: Practitioner
    """
    practitioner = odh.create_practitioner_resource(resource_id="practitioner-1", national_identifier="4826940",
                                                    local_identifier="281")
    return practitioner
