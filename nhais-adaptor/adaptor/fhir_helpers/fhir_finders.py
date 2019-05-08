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
