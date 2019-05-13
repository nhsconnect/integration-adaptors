import logging

from builder.pystache_message_builder import PystacheMessageBuilder
from definitions import TEMPLATE_PATH, XML_PATH
from utilities.file_utilities import FileUtilities
from abc import ABC, abstractmethod


class Check(ABC):

    distribution_envelope = "./soap:Body/itk:DistributionEnvelope"
    soap_body = "./soap:Body"
    manifest_tag = distribution_envelope + "/itk:header/itk:manifest"
    basic_success_message = FileUtilities.get_file_string(str(XML_PATH / 'basic_success_response.xml'))

    namespaces = {
        'soap': 'http://schemas.xmlsoap.org/soap/envelope/',
        'a': 'http://www.etis.fskab.se/v1.0/ETISws',
        'wsa': 'http://www.w3.org/2005/08/addressing',
        'itk': 'urn:nhs-itk:ns:201005'
    }

    def __init__(self, message):
        self.message_tree = message

    @abstractmethod
    def check(self):
        """
        An asbtract method called by the validator to run the check
        :return: flail flag, error message
        """
        pass

    def get_manifest_count(self):
        """
        Extracts the count on the manifest tag in the message
        :return: manifest count as a string
        """
        return self.message_tree.find(self.distribution_envelope + "/itk:header/itk:manifest",
                                      self.namespaces).attrib['count']

    def get_payload_count(self):
        """
        Extracts the count on the payloads tag in the message
        :return: payloads count as a string
        """
        return self.message_tree.findall(self.distribution_envelope + "/itk:payloads", self.namespaces).attrib['count']

    def build_error_message(self, error):
        builder = PystacheMessageBuilder(str(TEMPLATE_PATH), 'base_error_template')
        return builder.build_message({"errorMessage": error})
