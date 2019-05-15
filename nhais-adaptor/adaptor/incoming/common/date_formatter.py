from datetime import datetime


def format_date_time(edifact_date_time):
    """
    format the edifact date time to a fhir format
    :param edifact_date_time: The incoming date time stamp from the interchange header
    :return: The formatted date time stamp
    """
    current_format = "%y%m%d:%H%M"
    desired_format = "%Y-%m-%d %H:%M"
    formatted_date = datetime.strptime(edifact_date_time, current_format).strftime(desired_format)
    return formatted_date
