from fhirclient.models.humanname import HumanName
from fhirclient.models.identifier import Identifier
from fhirclient.models.operationdefinition import OperationDefinitionParameterBinding, OperationDefinitionParameter, \
    OperationDefinition
from fhirclient.models.patient import Patient
from fhirclient.models.practitioner import Practitioner
from fhirclient.models.address import Address
from fhirclient.models.extension import Extension


class OperationName:
    """
    Constants for the type of fhir operations the adaptor can use
    """
    REGISTER_BIRTH = "RegisterPatient-Birth"


class ParameterName:
    """
    Constants for parameter names used in the adaptor
    """
    INTERCHANGE_SEQ_NO = "interchangeSequenceNumber"
    SENDER_CYPHER = "senderCypher"
    MESSAGE_SEQ_NO = "messageSequenceNumber"
    NHAIS_CYPHER = "nhaisCypher"
    TRANSACTION_NO = "transactionNumber"
    REGISTER_PATIENT = "registerPatient"
    REGISTER_PRACTITIONER = "registerPractitioner"


class ResourceType:
    """
    Constants for the resource types used in the adaptor
    """
    PATIENT = "Patient"
    PRACTITIONER = "Practitioner"


def create_parameter_with_binding(name, value):
    """
    Helper function to create a fhir parameter with binding value
    :param name: name of the parameter
    :param value: the value of the parameter
    :return: OperationDefinitionParameter
    """
    identifier = Identifier({'value': value})
    op_param_binding = OperationDefinitionParameterBinding(
        {'strength': 'required', 'valueSetReference': {'identifier': identifier.as_json()}}
    )
    op_param = OperationDefinitionParameter(
        {'name': name, 'use': 'in', 'min': 1, 'max': '1',
         'binding': op_param_binding.as_json()})

    return op_param


def create_parameter_with_resource_ref(name, resource_type, reference):
    """
    Helper function to create a parameter with a reference to a resource
    :param name: the name of the parameter
    :param resource_type: the type of resource
    :param reference: reference to the resource
    :return: OperationDefinitionParameter
    """
    op_param = OperationDefinitionParameter(
        {'name': name, 'use': 'in', 'min': 1, 'max': '1', 'type': resource_type,
         'profile': {'reference': f"#{reference}"}})
    return op_param


def create_operation_definition(name, code, date_time, contained, parameters):
    """
    Helper function to create a fhir operation definition
    :param name: The name of the operation
    :param code: The code of the operation
    :param date_time: the time stamp of the operation
    :param contained: list of contained resources
    :param parameters: list of parameters
    :return: OperationDefinition
    """
    op = OperationDefinition(
        {'name': name,
         'kind': 'operation',
         'type': True,
         'system': False,
         'instance': False,
         'date': date_time,
         'status': 'active',
         'code': code})
    if len(contained) > 0:
        op.contained = contained
    if len(parameters) > 0:
        op.parameter = parameters
    return op


def create_practitioner_resource(resource_id, national_identifier, local_identifier):
    """
    Helper function to create a fhir Practitioner resource
    :return: Practitioner
    """
    practitioner = Practitioner({
        'id': resource_id,
        'identifier': [
            {
                'type': {
                    'coding': [{'code': 'national'}],
                    'text': 'GMC National code'
                },
                'value': national_identifier
            },
            {
                'type': {
                    'coding': [{'code': 'local'}],
                    'text': 'Local GP Code'
                },
                'value': local_identifier
            }
        ]
    })
    return practitioner


def create_patient_resource(resource_id, nhs_number, title, first_name, last_name, gender, date_of_birth,
                            address_line_1, city, postcode, place_of_birth):
    """
    Helper function to create a basic fhir patient
    :return: Patient
    """
    pat_address = Address({'line': [address_line_1], 'city': city, 'postalCode': postcode})
    nhs_number = Identifier({'value': nhs_number})
    name = HumanName({'prefix': [title], 'family': last_name, 'given': [first_name]})
    birth_address = Address({'city': place_of_birth})
    place_of_birth = Extension({'url': 'http://hl7.org/fhir/StructureDefinition/birthPlace',
                                'valueAddress': birth_address.as_json()})
    patient = Patient({'id': resource_id,
                       'identifier': [nhs_number.as_json()],
                       'gender': gender,
                       'name': [name.as_json()],
                       'birthDate': date_of_birth,
                       'address': [pat_address.as_json()],
                       'extension': [place_of_birth.as_json()]})
    return patient
