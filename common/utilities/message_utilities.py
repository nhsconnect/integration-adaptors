import uuid
import datetime
import utilities.file_utilities as file_utilities

EBXML_TIMESTAMP_FORMAT = "%Y-%m-%dT%H:%M:%SZ"


def get_uuid():
    """Generate a UUID suitable for sending in messages to Spine.

    :return: A string representation of the UUID.
    """
    return str(uuid.uuid4()).upper()


def get_timestamp():
    """Generate a timestamp in a format suitable for sending in ebXML messages.

    :return: A string representation of the timestamp
    """

    current_utc_time = datetime.datetime.utcnow()
    return current_utc_time.strftime(EBXML_TIMESTAMP_FORMAT)


def load_test_data(message_dir, filename_without_extension):
    message = file_utilities.get_file_string(message_dir / (filename_without_extension + ".msg"))
    ebxml = file_utilities.get_file_string(message_dir / (filename_without_extension + ".ebxml"))

    message = message.replace("{{ebxml}}", ebxml)

    return message, ebxml
