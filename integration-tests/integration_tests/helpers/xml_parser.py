import xml.etree.ElementTree as et

HL7_NAMESPACE = "hl7"
NAMESPACES = {HL7_NAMESPACE: "urn:hl7-org:v3"}


class XmlMessageParser:
    """A component that extracts information from XML messages."""

    def parse_message(self, message):
        """ Parse the provided XML message and extract a dictionary of values from it.

        :param message: The message to be parsed.
        :return: the parsed message.
        """
        return et.fromstring(message)

    def path_to_hl7xml_element(self, name, parent=None):
        """ Build the X-Path for the element

        :param name: the name ot the element
        :param parent: name of the elements parent
        :return: the X-Path
        """
        path = ".//"

        if parent is not None:
            path += HL7_NAMESPACE + ":" + parent + "/"

        path += HL7_NAMESPACE + ":" + name

        return path

    def extract_hl7xml_section(self, xml_tree, element_name, parent=None):
        """ Extract a section of the XML

        :param xml_tree: the parsed XML
        :param element_name: the name ot the element
        :param parent: name of the elements parent
        :return: the extracted section
        """
        xpath = self.path_to_hl7xml_element(element_name, parent=parent)
        return xml_tree.find(xpath, namespaces=NAMESPACES)

    def extract_hl7xml_text_value(self, xml_tree, attribute, element_name, parent=None):
        """ Extract the value of an attribute

        :param xml_tree: the parsed XML
        :param attribute: the name of the attribute
        :param element_name: the name ot the element
        :param parent: name of the elements parent
        :return: the extracted value
        """
        value = self.extract_hl7xml_section(xml_tree, element_name, parent)
        text = None

        if value is not None:
            text = value.attrib[attribute]

        return text
