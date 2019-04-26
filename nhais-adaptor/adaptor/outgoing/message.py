from edifact.models.message import MessageSegmentPatientDetails
from edifact.models.name import Name
from edifact.models.address import Address


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
        edi_address = Address(house_name="",
                              address_line_1=fhir_patient_address.line[0],
                              address_line_2=fhir_patient_address.line[1],
                              town=fhir_patient_address.city,
                              county=fhir_patient_address.district,
                              post_code=fhir_patient_address.postalCode)
        return edi_address

    @staticmethod
    def create_message_segment_patient_detail(fhir_patient):
        """
        :param fhir_patient: the fhir representation of the patient details
        :return: MessageSegmentPatientDetails
        """

        print(fhir_patient.as_json())

        edi_name = MessageAdaptor.create_patient_name(fhir_patient.name[0])

        edi_address = MessageAdaptor.create_patient_address(fhir_patient.address[0])

        # get nhs number, date or birth and gender
        msg_seg_patient_details = MessageSegmentPatientDetails(id_number=fhir_patient.identifier[0].value,
                                                               name=edi_name,
                                                               date_of_birth="2019-04-23",
                                                               gender=fhir_patient.gender,
                                                               address=edi_address)
        return msg_seg_patient_details
