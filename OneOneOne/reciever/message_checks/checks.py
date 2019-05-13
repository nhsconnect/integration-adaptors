from reciever.message_checks.Check import Check
import logging


class CheckManifestCountInstances(Check):

    def __init__(self, message):
        super(CheckManifestCountInstances, self).__init__(message)

    def check(self):
        """
       Checks if the manifest.count attribute matches the number of manifest items as per the 'DE_INVMCT'
       spec, returns a failure flag where True indicates a failure has occurred
       :return: failure flag, response content
       """
        manifest_count = int(self.get_manifest_count())

        manifest_actual_count = len(self.message_tree.findall(self.manifest_tag + "/itk:manifestitem", self.namespaces))
        if manifest_count != manifest_actual_count:
            logging.warning("Manifest count did not equal number of instances: (expected : found) - (%i : %i)",
                            manifest_count, manifest_actual_count)

            return True, "The number of manifest instances does not match the manifest count specified"

        return False, None


class CheckActionTypes(Check):

    def __int__(self, message):
        super(CheckActionTypes, self).__init__(message)

    def check(self):
        """
       This method checks for equality between the action type in the header, and the service value in the message
       body as per the 'DE_INVSER' requirement specified in the requirements spreadsheet
       Returns a failure flag where True indicates a failure has occurred
       :return: failure flag, response content
       """
        action_tag_value = "-"
        for type_tag in self.message_tree.findall("./soap:Header/wsa:Action", self.namespaces):
            action_tag_value = type_tag.text

        service_tag_value = "+"
        for type_tag in self.message_tree.findall(self.distribution_envelope + '/itk:header', self.namespaces):
            service_tag_value = type_tag.attrib['service']

        if action_tag_value != service_tag_value:
            logging.warning("Action type does not match service type: (Action Tag, Service Tag) (%s, %s)",
                            action_tag_value,
                            service_tag_value)
            return True,  "Manifest action does not match service action"

        return False, None


class CheckManifestPayloadCounts(Check):

    def __init__(self, message):
        super(CheckManifestPayloadCounts, self).__init__(message)

    def check(self):
        """
        This verifies the manifest count is equal to the payload count as per 'DE_INVMPC' requirement
        :return: status code, response content
        """

        manifest_count = self.get_manifest_count()

        payload_count = self.get_payload_count()

        if payload_count != manifest_count:
            logging.warning("Error in manifest count: (ManifestCount, PayloadCount) (%s, %s)", manifest_count,
                            payload_count)
            return True, "Manifest count does not match payload count"

        return False, None


class CheckPayloadCountAgainstActual(Check):

    def __init__(self, message):
        super(CheckPayloadCountAgainstActual, self).__init__(message)

    def check(self):
        """
        Checks if the specified payload count matches the actual occurrences of payload elements
        as per 'DE_INVPCT' in the spec
        :return: status code, response content
        """
        payload_count = int(self.get_payload_count())

        payload_actual_count = len(self.message_tree.findall(self.distribution_envelope + "/itk:payloads/itk:payload",
                                                             self.namespaces))
        if payload_count != payload_actual_count:
            logging.warning("Payload count does not match number of instances - Expected: %i Found: %i",
                            payload_count,
                            payload_actual_count)
            return True, "Invalid message"

        return False, None


class CheckPayloadIdAgainstManifestId(Check):

    def __init__(self, message):
        super(CheckPayloadIdAgainstManifestId, self).__init__(message)

    def check(self):
        """
        Checks that for each id of each manifest item has a corresponding
        payload with the same Id as per  'DE_INVMPI'
        :return: status code, response content
        """
        payload_ids = set()
        manifest_ids = set()
        for payload in self.message_tree.findall(self.distribution_envelope + "/itk:payloads/itk:payload",
                                                 self.namespaces):
            payload_ids.add(payload.attrib['id'])

        for manifest in self.message_tree.findall(self.manifest_tag + "/itk:manifestitem",
                                                  self.namespaces):
            manifest_ids.add(manifest.attrib['id'])

        if len(payload_ids.difference(manifest_ids)) != 0:
            logging.warning("Payload IDs do not match Manifest IDs")
            return True, "Payload IDs do not map to Manifest IDs"

        return False, None
