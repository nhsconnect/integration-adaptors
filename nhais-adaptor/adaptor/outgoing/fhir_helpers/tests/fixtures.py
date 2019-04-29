from adaptor.outgoing.fhir_helpers.operation_definition import OperationDefinitionHelper as odh


class Fixtures:
    """
    Class to help create fhir test fixtures
    """

    @staticmethod
    def create_simple_patient():
        """
        creates a simple fhir patient with no previous names or addresses
        :return: Patient
        """
        patient = odh.create_patient_resource(resource_id="patient-1", nhs_number="NHSNO11111",
                                              title="Mr", first_name="Peter", last_name="Parker",
                                              gender="male", date_of_birth="2019-04-23",
                                              place_of_birth="Spidey Town",
                                              address_line_1="1 Spidey Way", city="Spidey Town", postcode="SP1 1AA")
        return patient

