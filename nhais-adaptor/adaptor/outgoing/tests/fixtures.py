import adaptor.outgoing.fhir_helpers.fhir_creators as creators
from adaptor.outgoing.fhir_helpers.fhir_creators import OperationName
from adaptor.outgoing.fhir_helpers.fhir_creators import ParameterName, ResourceType


def create_simple_patient():
    """
    creates a simple fhir patient with no previous names or addresses
    :return: Patient
    """
    patient = creators.create_patient_resource(resource_id="patient-1", nhs_number="NHSNO11111",
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
    practitioner = creators.create_practitioner_resource(resource_id="practitioner-1", national_identifier="4826940",
                                                         local_identifier="281")
    return practitioner


def create_operation_definition_for_birth_registration():
    """
    Creates an fhir operation definition for a birth registration
    :return: OperationDefinition
    """
    op_param_interchange_sequence = creators.create_parameter_with_binding(
        name=ParameterName.INTERCHANGE_SEQ_NO,
        value="000001")
    op_param_sender_cypher = creators.create_parameter_with_binding(name=ParameterName.SENDER_CYPHER,
                                                                    value="TES5")
    op_param_message_sequence = creators.create_parameter_with_binding(name=ParameterName.MESSAGE_SEQ_NO,
                                                                       value="000001")
    op_param_nhais_cypher = creators.create_parameter_with_binding(name=ParameterName.NHAIS_CYPHER, value="XX1")
    op_param_transaction_number = creators.create_parameter_with_binding(name=ParameterName.TRANSACTION_NO,
                                                                         value="17")
    practitioner = create_simple_practitioner()
    patient = create_simple_patient()
    op_param_practitioner = creators.create_parameter_with_resource_ref(
        name=ParameterName.REGISTER_PRACTITIONER,
        resource_type=ResourceType.PRACTITIONER,
        reference="practitioner-1")
    op_param_patient = creators.create_parameter_with_resource_ref(name=ParameterName.REGISTER_PATIENT,
                                                                   resource_type=ResourceType.PATIENT,
                                                                   reference="patient-1")
    op_def = creators.create_operation_definition(name=OperationName.REGISTER_BIRTH, code="gpc.registerpatient",
                                                  date_time="2019-04-23 09:00:04.159338",
                                                  contained=[practitioner, patient],
                                                  parameters=[op_param_interchange_sequence,
                                                              op_param_sender_cypher,
                                                              op_param_message_sequence,
                                                              op_param_transaction_number,
                                                              op_param_nhais_cypher,
                                                              op_param_practitioner, op_param_patient])

    return op_def
