from datetime import datetime


def format_date(date_time, format_qualifier="DEFAULT", current_format="%Y-%m-%d %H:%M:%S.%f"):
    """
    :param date_time: the date time stamp to format
    :param format_qualifier: the edifact format qualifier eg 203 or 102
    :param current_format: the current format of the date_time param
    :return: the formatted date as a string
    """
    format_qualifier_dict = {
        '203': '%Y%m%d%H%M',
        '102': '%Y%m%d',
        'DEFAULT': '%y%m%d:%H%M'
    }
    date_formatter = format_qualifier_dict[format_qualifier]
    formatted_date = datetime.strptime(date_time, current_format).strftime(date_formatter)
    return formatted_date
