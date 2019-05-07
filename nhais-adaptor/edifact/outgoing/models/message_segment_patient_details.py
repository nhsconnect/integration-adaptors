from edifact.helpers import date_formatter as date_formatter
from edifact.outgoing.models.address import PatientAddress
from edifact.outgoing.models.name import PatientName
from edifact.outgoing.models.segment import SegmentCollection, Segment


class MessageSegmentPatientDetails(SegmentCollection):
    """
    A collection of segments that represent personal information about a patient.
    """

    def __init__(self):
        segments = [
            Segment(key="S02", value="2"),
        ]
        super().__init__(segments=segments)


class MessageSegmentBirthPatientDetails(MessageSegmentPatientDetails):
    """
    A specialisation of the MessageSegmentPatientDetails class for the purpose of a Birth
    """

    def __init__(self, id_number, name, date_of_birth, gender, address):
        """
        :param id_number: OPI official Payment Id (existing NHS Number)
        :param name: the name of the patient
        :param date_of_birth: Patients date of birth
        :param gender: sex of the patient. For an acceptance transaction, reference "G1", this segment is required
        :param address: the patients address
        """
        formatted_date = date_formatter.format_date(date_time=date_of_birth, format_qualifier="102",
                                                    current_format="%Y-%m-%d")
        segments = [
            PatientName(id_number=id_number, name=name),
            Segment(key="DTM", value=f"329:{formatted_date}:102"),
            Segment(key="PDI", value=f"{gender}"),
            PatientAddress(address=address)
        ]
        super().__init__()
        super().add_segments(segments)


class MessageSegmentDeathPatientDetails(MessageSegmentPatientDetails):
    """
    A specialisation of the MessageSegmentPatientDetails class for the purpose of a Death
    """

    def __init__(self, id_number):
        """
        :param id_number: OPI official Payment Id (existing NHS Number)
        """
        segments = [
            Segment(key="PNA", value=f"PAT+{id_number}:OPI"),
        ]
        super().__init__()
        super().add_segments(segments)