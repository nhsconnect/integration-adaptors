from fhirclient.models.humanname import HumanName
from fhirclient.models.identifier import Identifier
from fhirclient.models.operationdefinition import OperationDefinitionParameterBinding, OperationDefinitionParameter, \
    OperationDefinition
from fhirclient.models.patient import Patient
from fhirclient.models.practitioner import Practitioner
from fhirclient.models.address import Address
from fhirclient.models.extension import Extension


class OperationDefinitionHelper:

    @staticmethod
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

    @staticmethod
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

    @staticmethod
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

    @staticmethod
    def create_practitioner_resource(resource_id, national_identifier, local_identifier):
        """
        Helper function to create a fhir Practitioner resource
        :param resource_id: the id of the resource
        :param national_identifier: the national identifier
        :param local_identifier: the local identifier
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

    @staticmethod
    def create_patient_resource(resource_id, nhs_number, title, first_name, last_name, gender, date_of_birth,
                                address_line_1, city, postcode, place_of_birth):
        """
        Helper function to create a basic fhir patient
        :param resource_id: the id of the resource
        :param nhs_number: the nhs number of the patient
        :param title: title of the patient
        :param first_name: first name of the patient
        :param last_name: last name of the patient
        :param gender: patient gender
        :param date_of_birth: date of birth of patient
        :param address_line_1: first line of address
        :param city: city of patient
        :param postcode: post code of patient
        :param place_of_birth: place of birth of patient
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

    @staticmethod
    def get_parameter_value(fhir_operation, parameter_name):
        """
        Find the parameter value provided in the parameters
        :param fhir_operation: the fhir operation definition
        :param parameter_name: the name of the parameter to get the value of
        :return: a string representation of th value
        """
        parameter_value = ''
        for param in fhir_operation.parameter:
            if param.name == parameter_name:
                parameter_value = param.binding.valueSetReference.identifier.value
        return parameter_value

    @staticmethod
    def find_resource(fhir_operation, resource_type):
        """
        From the parameter get the resource in the contained list
        :param fhir_operation:
        :param resource_type: the resource type to find
        :return: Practitioner
        """
        resource_reference = ""
        for param in fhir_operation.parameter:
            if param.type == resource_type:
                resource_reference = param.profile.reference

        found_resource = None
        for resource in fhir_operation.contained:
            if f"#{resource.id}" == resource_reference:
                found_resource = resource

        return found_resource
