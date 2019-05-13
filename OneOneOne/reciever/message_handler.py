import xml.etree.ElementTree as ET

from builder.pystache_message_builder import PystacheMessageBuilder
from reciever.message_checks.checks import *
from reciever.message_checks.Check import Check
from utilities.file_utilities import FileUtilities
from definitions import XML_PATH, TEMPLATE_PATH
import logging
from typing import List, Type
from reciever.message_validator import MessageValidator

CheckList = List[Type[Check]]

basic_success_response = FileUtilities.get_file_string(XML_PATH / 'basic_success_response.xml')


def build_error_message(error):
    builder = PystacheMessageBuilder(str(TEMPLATE_PATH), 'base_error_template')
    return builder.build_message({"errorMessage": error})


class MessageHandler:
    """
        Validates the incoming message and wraps the validation outcome in a response
        to be returned to the sender
    """

    def __init__(self, message):
        self.message_tree = ET.fromstring(message)
        self.validator = MessageValidator(self.message_tree)
        self.error_flag, self.error_message = self.validator.evaluate_message()
        if not self.error_flag:
            self.handle()

    def get_response(self):
        """
        Returns a fully wrapped error/success response for the given message
        :return: string
        """
        if self.error_flag:
            return build_error_message(self.error_message)
        else:
            return basic_success_response

    def get_response_code(self):
        """
        Determines the http response code based on the failure flag set by validation
        :return: http response code
        """
        if self.error_flag:
            return 500
        else:
            return 200

    def handle(self):
        """
        This is an empty method meant as a placeholder for whatever asynchronous message/parsing would occur after the
        incoming message has been identified as valid and the sender has been notified as such
        :return:
        """
        pass
