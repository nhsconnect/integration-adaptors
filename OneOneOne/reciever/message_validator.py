from reciever.message_checks.checks import *
from typing import List

CheckList = List[Check]
check_list = [CheckManifestCountInstances, CheckActionTypes, CheckManifestPayloadCounts,
              CheckPayloadCountAgainstActual, CheckPayloadIdAgainstManifestId
              ]


class MessageValidator:

    def __init__(self, message_tree, checks: CheckList = check_list):
        self.message_tree = message_tree
        self.check_list = checks

    def evaluate_message(self):
        """
        This iterates over the message check methods searching for errors in the message, if no errors are found
        a success response is returned

        :return: status code, response content
        """

        for check in self.check_list:
            c = check(self.message_tree)  # instantiate the check object instance
            fail, response = c.check()  # make the check call
            if fail:
                return fail, response

        return False, None
