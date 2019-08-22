import datetime

from selenium_tests.page_objects import methods, logs_retriever
from unittest import TestCase

LOG_DIR = "selenium_tests/data"
LOG_FILENAME = "test.txt"

TIMESTAMP_FORMAT = "%Y-%m-%dT%H:%M:%S.%f"


class FunctionalTest(TestCase):

    def test_logging_file(self):
        # start the clock
        start_time = datetime.datetime.utcnow()
        print('Time test started: ', start_time.strftime(TIMESTAMP_FORMAT))

        # fire off an (MHS) action that will generate a log file
        interaction_name = 'gp_summary_upload'
        nhs_number = '9446245796'
        methods.get_interaction(interaction_name, nhs_number)

        # stop the clock
        end_time = datetime.datetime.utcnow()
        print('Time test ended: ', end_time.strftime(TIMESTAMP_FORMAT))

        # get the log file
        logs = logs_retriever.get_logs(logs_retriever.Component.MHS)

        # check the timestamps in the log file are between the start & end times
        for line in logs:
            # extract the timestamp from the line...
            time = methods.get_log_timestamp(line)
            print('Timestamp: ', time)

            after_start = time > start_time.strftime(TIMESTAMP_FORMAT)
            before_end = end_time.strftime(TIMESTAMP_FORMAT) > time
            self.assertTrue(after_start and before_end)
