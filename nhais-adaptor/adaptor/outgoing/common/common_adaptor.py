from edifact.outgoing.models.address import Address
from edifact.outgoing.models.name import Name


def create_patient_name(fhir_patient_name):
    """
    Function to generate the edifact representation of the patient name
    :param fhir_patient_name: fhir representation of the patient name
    :return: edifact name
    """
    given_names = [None, None, None]
    for index, given_name in enumerate(fhir_patient_name.given):
        given_names[index] = given_name

    edi_name = Name(title=fhir_patient_name.prefix[0],
                    family_name=fhir_patient_name.family,
                    first_given_forename=fhir_patient_name.given[0],
                    middle_name=given_names[1],
                    third_given_forename=given_names[2])
    return edi_name


def determine_address_lines(fhir_patient_address_lines):
    """
    This function generates a uniform list of address lines always returning a list of 3 lines.
    The result of this can be used to populate the edifact address model
    Since the fhir patient address does not have anything specifically for house name in its definition.
    This function assumes that if 3 address lines are provided then the first line is the house name
    if it is less than 3 then always default the first line as "".
    :param fhir_patient_address_lines: the fhir representation for the patient address
    :return: a uniform list of address lines to populate the edifact address model
    """
    address_lines = ["", "", ""]
    counter = 0 if len(fhir_patient_address_lines) == 3 else 1

    for line in fhir_patient_address_lines:
        address_lines[counter] = line
        counter += 1

    return address_lines


def create_patient_address(fhir_patient_address):
    """
    Function to generate the edifact representation of the patient address
    :param fhir_patient_address: The fhir representation of the patient address
    :return: edifact address
    """
    address_lines = determine_address_lines(fhir_patient_address.line)

    edi_address = Address(house_name=address_lines[0],
                          address_line_1=address_lines[1],
                          address_line_2=address_lines[2],
                          town=fhir_patient_address.city,
                          county=fhir_patient_address.district if fhir_patient_address.district else "",
                          post_code=fhir_patient_address.postalCode)
    return edi_address
