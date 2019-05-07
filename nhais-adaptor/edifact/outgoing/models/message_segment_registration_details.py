from edifact.helpers import date_formatter as date_formatter
from edifact.outgoing.models.segment import SegmentCollection, Segment


class MessageSegmentRegistrationDetails(SegmentCollection):
    """
    A collection of segments to provide registration information for GP patients.
    This is referred to in edifact as segment trigger 1
    """

    def __init__(self, transaction_number, party_id):
        """
        :param transaction_number: a unique transaction number. NHAIS will reference this in its response
        :param party_id: GMC National code and the Local GP Code of the patient's GP (separated by “,”).
        """
        segments = [
            Segment(key="S01", value="1"),
            Segment(key="RFF", value=f"TN:{transaction_number}"),
            Segment(key="NAD", value=f"GP+{party_id}:900"),
        ]
        super().__init__(segments=segments)


class MessageSegmentBirthRegistrationDetails(MessageSegmentRegistrationDetails):
    """
    A specialisation of the MessageSegmentRegistrationDetails class for the purpose of a Birth
    """

    def __init__(self, transaction_number, party_id, acceptance_code, acceptance_type, date_time, location):
        """
        :param transaction_number: a unique transaction number. NHAIS will reference this in its response
        :param party_id: GMC National code and the Local GP Code of the patient's GP (separated by “,”).
        :param acceptance_code: The acceptance code "A" for Acceptance
        :param acceptance_type: The acceptance type "1" for a Birth
        :param date_time: date of the registration
        :param location: the patients place of birth
        """
        formatted_date_time = date_formatter.format_date(date_time=date_time, format_qualifier="102")
        segments = [
            Segment(key="HEA", value=f"ACD+{acceptance_code}:ZZZ"),
            Segment(key="HEA", value=f"ATP+{acceptance_type}:ZZZ"),
            Segment(key="DTM", value=f"956:{formatted_date_time}:102"),
            Segment(key="LOC", value=f"950+{location}"),
        ]
        super().__init__(transaction_number=transaction_number, party_id=party_id)
        super().add_segments(segments)


class MessageSegmentDeathRegistrationDetails(MessageSegmentRegistrationDetails):
    """
    A specialisation of the MessageSegmentRegistrationDetails class for the purpose of a Death
    """

    def __init__(self, transaction_number, party_id, date_time, free_text=None):
        """
        :param transaction_number: a unique transaction number. NHAIS will reference this in its response
        :param party_id: GMC National code and the Local GP Code of the patient's GP (separated by “,”).
        :param date_time: date of the registration
        :param free_text: optional free text
        """
        formatted_date_time = date_formatter.format_date(date_time=date_time, format_qualifier="102")
        segments = [
            Segment(key="GIS", value=f"1:ZZZ"),
            Segment(key="DTM", value=f"961:{formatted_date_time}:102"),
        ]
        if free_text:
            segments.append(
                Segment(key="FTX", value=f"RGI+++{free_text}")
            )
        super().__init__(transaction_number=transaction_number, party_id=party_id)
        super().add_segments(segments)