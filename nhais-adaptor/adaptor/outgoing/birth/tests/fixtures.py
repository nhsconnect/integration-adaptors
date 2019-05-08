from adaptor.fhir_helpers import fhir_creators as creators
from adaptor.fhir_helpers.fhir_creators import ParameterName, ResourceType, OperationName
from adaptor.outgoing.tests.fixtures import create_simple_practitioner, create_simple_patient


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
                                                  parameters=[op_param_interchange_sequence,
                                                              op_param_sender_cypher,
                                                              op_param_message_sequence,
                                                              op_param_transaction_number,
                                                              op_param_nhais_cypher,
                                                              op_param_practitioner, op_param_patient],
                                                  contained=[practitioner, patient])

    return op_def