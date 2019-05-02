from tornado.httpserver import HTTPServer
import tornado.ioloop
import tornado.web
from lxml import etree
import xml.etree.ElementTree as ET
from utilities.file_utilities import FileUtilities
from definitions import XML_PATH

basic_success_response = FileUtilities.get_file_string(XML_PATH / 'basic_success_response.xml')

wrong_service_body = FileUtilities.get_file_string(XML_PATH / 'mismatched_action_services.xml')

wrong_manifest_count = FileUtilities.get_file_string(XML_PATH / 'manifest_not_equal_to_payload_count.xml')


class MessageHandler:
    namespaces = {
        'soap': 'http://schemas.xmlsoap.org/soap/envelope/',
        'a': 'http://www.etis.fskab.se/v1.0/ETISws',
        'wsa': 'http://www.w3.org/2005/08/addressing',
        'itk': 'urn:nhs-itk:ns:201005'
    }

    def __init__(self, message_string):
        self.message = message_string
        self.message_tree = ET.fromstring(self.message)

    def evaluate_message(self):
        status, response = self.check_action_types()
        if status != 200:
            return status, response

        status, response = self.check_manifest_and_payload_count()
        if status != 200:
            return status, response

        return 200, basic_success_response

    def check_action_types(self):
        """
        This method checks for equality between the action type in the header, and the service value in the message
        body as per the 'DE_INVSER' requirement specified in the requirements spreadsheet
        :return: status code, response content
        """
        header_action = ""
        for type_tag in self.message_tree.findall("./soap:Header"
                                                  "/wsa:Action",
                                                  self.namespaces):
            header_action = type_tag.text

        body_service = ""
        for type_tag in self.message_tree.findall('./soap:Body'
                                                  '/itk:DistributionEnvelope'
                                                  '/itk:header',
                                                  self.namespaces):
            body_service = type_tag.attrib['service']

        if header_action != body_service:
            return 500, wrong_service_body

        return 200, basic_success_response

    def check_manifest_and_payload_count(self):
        """
        This verifies the manifest count is equal to the payload count as per 'DE_INVMPC' requirement
        :return:
        """

        manifest_count = "-"
        for type_tag in self.message_tree.findall("./soap:Body"
                                                  "/itk:DistributionEnvelope"
                                                  "/itk:header"
                                                  "/itk:manifest",
                                                  self.namespaces):
            manifest_count = type_tag.attrib['count']

        payload_count = "+"
        for type_tag in self.message_tree.findall("./soap:Body"
                                                  "/itk:DistributionEnvelope"
                                                  "/itk:payloads",
                                                  self.namespaces):
            payload_count = type_tag.attrib['count']

        if payload_count != manifest_count:
            return 500, wrong_manifest_count

        return 200, basic_success_response
