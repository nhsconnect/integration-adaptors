import xml.etree.ElementTree as ET

from builder.pystache_message_builder import PystacheMessageBuilder
from reciever.message_checks.checks import *
from reciever.message_checks.check import Check
from utilities.file_utilities import FileUtilities
from OneOneOne.definitions import XML_PATH, TEMPLATE_PATH
from typing import List, Type

basic_success_response = FileUtilities.get_file_string(XML_PATH / 'basic_success_response.xml')

check_list = [CheckManifestCountInstances, CheckActionTypes, CheckManifestPayloadCounts,
              CheckPayloadCountAgainstActual, CheckPayloadIdAgainstManifestId
              ]


def build_error_message(error):
    builder = PystacheMessageBuilder(str(TEMPLATE_PATH), 'base_error_template')
    return builder.build_message({"errorMessage": error})


class MessageHandler:
    """
    Validates the incoming message and wraps the validation outcome in a response
    to be returned to the sender
    """

    def __init__(self, message, checks: List[Type[Check]] = check_list):
        self.message_tree = ET.fromstring(message)
        self.check_list = checks
        self.error_flag = False
        self.response_message = None
        self.evaluate_message()
        if not self.error_flag:
            self.handle()

    def get_response(self):
        """
        Returns a fully wrapped error/success response for the given message
        :return: string
        """
        if self.error_flag:
            return build_error_message(self.response_message)
        else:
            return basic_success_response

    def handle(self):
        """
        This is an empty method meant as a placeholder for whatever asynchronous message/parsing would occur after the
        incoming message has been identified as valid and the sender has been notified as such
        :return:
        """
        pass

    def evaluate_message(self):
        """
        This iterates over the message check methods searching for errors in the message, if no errors are found
        a success response is returned

        :return: status code, response content
        """

        for check in self.check_list:
            c = check(self.message_tree)  # instantiate the check object instance
            fail, response_string = c.check()  # make the check call
            if fail:
                self.error_flag = True
                self.response_message = response_string
                return

        return False, None
