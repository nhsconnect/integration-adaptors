import uuid
import datetime

EBXML_TIMESTAMP_FORMAT = "%Y-%m-%dT%H:%M:%SZ"


class MessageUtilities:
    @staticmethod
    def get_uuid():
        """Generate a UUID suitable for sending in messages to Spine.

        :return: A string representation of the UUID.
        """
        return str(uuid.uuid4()).upper()

    @staticmethod
    def get_timestamp():
        """Generate a timestamp in a format suitable for sending in ebXML messages.

        :return: A string representation of the timestamp
        """

        current_utc_time = datetime.datetime.utcnow()
        return current_utc_time.strftime(EBXML_TIMESTAMP_FORMAT)
