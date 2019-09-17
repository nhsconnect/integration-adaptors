from edifact.outgoing.models.segment import Segment


class Name(object):
    """
    A class to encapsulate the name attributes required for an edifact message
    """

    def __init__(self, family_name, first_given_forename, title, middle_name=None, third_given_forename=None):
        """
        :param family_name: Also know as the surname represented in edifact as SU
        :param first_given_forename: the 1st forename of the patient represented in edifact as FO
        :param title: the patients TITLE represented in edifact as TI
        :param middle_name: patients middle name represented in edifact as MI also called the 2nd given forename
        :param third_given_forename: Patients third given forename represented in edifact as FS
        """
        self.family_name = family_name
        self.first_given_forename = first_given_forename
        self.title = title
        self.middle_name = middle_name
        self.third_given_forename = third_given_forename


class PatientName(Segment):
    """
    A specialisation of the segment for the purpose of patient name and identification
    """

    SEGMENT_KEY = "PNA"

    def __init__(self, id_number, name):
        """
        :param id_number: The patient nhs number
        :param name: The name details
        """
        names = [f"SU:{name.family_name}", f"FO:{name.first_given_forename}", f"TI:{name.title}"]
        if name.middle_name:
            names.append(f"MI:{name.middle_name}")
        if name.third_given_forename:
            names.append(f"FS:{name.third_given_forename}")

        edifact_name = '+'.join(names)

        segment_value = f"PAT+{id_number}:OPI+++{edifact_name}"
        super().__init__(key=self.SEGMENT_KEY, value=segment_value)
