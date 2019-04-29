from edifact.models.message import MessageSegmentPatientDetails, MessageSegmentRegistrationDetails, MessageBeginning
from edifact.models.name import Name
from edifact.models.address import Address
from adaptor.outgoing.fhir_helpers.operation_definition import OperationDefinitionHelper as odh


class MessageAdaptor:
    """
    An adaptor to take in fhir model and generate and populate the edifact models
    """
    @staticmethod
    def create_patient_name(fhir_patient_name):
        given_names = [None, None, None]
        for index, given_name in enumerate(fhir_patient_name.given):
            given_names[index] = given_name

        edi_name = Name(title=fhir_patient_name.prefix[0],
                        family_name=fhir_patient_name.family,
                        first_given_forename=fhir_patient_name.given[0],
                        middle_name=given_names[1],
                        third_given_forename=given_names[2])
        return edi_name

    @staticmethod
    def create_patient_address(fhir_patient_address):

        address_lines = ["", "", ""]
        counter = 0 if len(fhir_patient_address.line) == 3 else 1

        for line in fhir_patient_address.line:
            address_lines[counter] = line
            counter += 1

        edi_address = Address(house_name=address_lines[0],
                              address_line_1=address_lines[1],
                              address_line_2=address_lines[2],
                              town=fhir_patient_address.city,
                              county=fhir_patient_address.district if fhir_patient_address.district else "",
                              post_code=fhir_patient_address.postalCode)
        return edi_address

    @staticmethod
    def create_message_segment_patient_detail(fhir_patient):
        """
        :param fhir_patient: the fhir representation of the patient details
        :return: MessageSegmentPatientDetails
        """
        gender_map = {'unknown': 0, 'male': 1, 'female': 2, 'other': 9}

        edi_name = MessageAdaptor.create_patient_name(fhir_patient.name[0])

        edi_address = MessageAdaptor.create_patient_address(fhir_patient.address[0])

        # get nhs number, date or birth and gender
        msg_seg_patient_details = MessageSegmentPatientDetails(id_number=fhir_patient.identifier[0].value,
                                                               name=edi_name,
                                                               date_of_birth=fhir_patient.birthDate.as_json(),
                                                               gender=gender_map[fhir_patient.gender],
                                                               address=edi_address)
        return msg_seg_patient_details

    @staticmethod
    def create_message_segment_registration_details(fhir_operation):
        """
        Create the message segment registration details from the fhir operation
        :param fhir_operation:
        :return: MessageSegmentRegistrationDetails
        """

        transaction_number = odh.get_parameter_value(fhir_operation=fhir_operation, parameter_name="transactionNumber")

        acceptance_code = ''
        acceptance_type = ''
        if fhir_operation.name == 'RegisterPatient-Birth':
            acceptance_code = "A"
            acceptance_type = "1"

        practitioner_details = odh.find_resource(fhir_operation=fhir_operation, resource_type="Practitioner")
        party_id = f"{practitioner_details.identifier[0].value},{practitioner_details.identifier[1].value}"

        patient_details = odh.find_resource(fhir_operation=fhir_operation, resource_type="Patient")
        birth_location = patient_details.extension[0].valueAddress.city

        msg_seg_registration_details = MessageSegmentRegistrationDetails(transaction_number=transaction_number,
                                                                         party_id=party_id,
                                                                         acceptance_code=acceptance_code,
                                                                         acceptance_type=acceptance_type,
                                                                         date_time=fhir_operation.date.as_json(),
                                                                         location=birth_location)
        return msg_seg_registration_details

    @staticmethod
    def create_message_beginning(fhir_operation):
        """
        Create the beginning of the message
        :param fhir_operation:
        :return: MessageBeginning
        """
        nhais_id = odh.get_parameter_value(fhir_operation=fhir_operation, parameter_name="nhaisCypher")

        ref_number = ''
        if fhir_operation.name == 'RegisterPatient-Birth':
            ref_number = "G1"

        msg_bgn = MessageBeginning(party_id=nhais_id, date_time=fhir_operation.date.as_json(), ref_number=ref_number)

        return msg_bgn


