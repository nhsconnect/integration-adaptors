from edifact.outgoing.models.segment import Segment


class Address:
    """
    A class to encapsulate the address attributes required for an edifact message
    """

    def __init__(self, house_name="", address_line_1="", address_line_2="", town="", county="", post_code=""):
        """
        :param house_name: the house name
        :param address_line_1: First line of address
        :param address_line_2: The second line of address
        :param town: The town
        :param county: The County
        :param post_code: The post_code
        """
        self.house_name = house_name
        self.address_line_1 = address_line_1
        self.address_line_2 = address_line_2
        self.town = town
        self.county = county
        self.post_code = post_code


class PatientAddress(Segment):
    """
    A specialisation of the segment for the purpose of a patient address details
    """

    SEGMENT_KEY = "NAD"

    def __init__(self, address):
        """
        :param address: The address details
        """
        segment_value = f"PAT++{address.house_name}:{address.address_line_1}:{address.address_line_2}:" \
            f"{address.town}:{address.county}+++++{address.post_code}"
        super().__init__(key=self.SEGMENT_KEY, value=segment_value)
