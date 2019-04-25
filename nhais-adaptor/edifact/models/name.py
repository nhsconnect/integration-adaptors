class Name:
    """
    A class to encapsulate the name attributes required for an edifact message
    """

    def __init__(self, family_name, first_given_forename, title, middle_name, third_given_forename):
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

