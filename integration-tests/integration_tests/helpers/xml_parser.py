import xml.etree.ElementTree as et

HL7_NAMESPACE = "hl7"
NAMESPACES = {HL7_NAMESPACE: "urn:hl7-org:v3"}


class XmlMessageParser:
    """A component that extracts information from XML messages."""

    def parse_message(self, message):
        """Parse the provided XML message and extract a dictionary of values from it.

        :param message: The message to be parsed.
        :return: the parsed message.
        """
        try:
            return et.fromstring(message)
        except:
            return None

    def path_to_hl7xml_element(self, name, parent=None):
        path = ".//"

        if parent is not None:
            path += HL7_NAMESPACE + ":" + parent + "/"

        path += HL7_NAMESPACE + ":" + name

        return path

    def extract_hl7xml_value(self, xml_tree, element_name, parent=None):
        xpath = self.path_to_hl7xml_element(element_name, parent=parent)
        return xml_tree.find(xpath, namespaces=NAMESPACES)

    def extract_hl7xml_text_value(self, xml_tree, element_name, parent=None):
        value = self.extract_hl7xml_value(xml_tree, element_name, parent)
        text = None

        if value is not None:
            text = value.text

        return text
