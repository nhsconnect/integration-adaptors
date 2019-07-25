import datetime

from definitions import ROOT_DIR
from pathlib import Path
from selenium_tests.page_objects import methods
from unittest import TestCase

# temp location/file to prove the tes works
# todo - extract the log file from Amazon CloudWatch
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

        # todo - remove this temp code
        # temp dirty code for testing with 'test.txt', which is a pseudo log file
        #   the stuff in this file contain 'log' between 2019-07-25T09:37:38.123456
        #   and 2019-07-25T09:47:59.678901...
        time = '2019-07-25T09:37:23.646564'
        start_time = datetime.datetime.strptime(time, TIMESTAMP_FORMAT)
        time = '2019-07-25T09:48:01.976354'
        end_time = datetime.datetime.strptime(time, TIMESTAMP_FORMAT)
        # end of temp code

        # get the log file
        # todo - this will need to change to retrieve to logfile from Amazon CloudWatch
        with open(str(Path(ROOT_DIR) / LOG_DIR / LOG_FILENAME)) as file:
            # check the timestamps in the log file are between the start & end times
            for line in file:
                # extract the timestamp from the line...
                time = methods.get_log_timestamp(line)
                print('Timestamp: ', time)
                level = methods.get_log_level(line)
                print('Log level: ', level)
                description = methods.get_log_description(line)
                print('Log description: ', description)
                after_start = time > start_time.strftime(TIMESTAMP_FORMAT)
                before_end = end_time.strftime(TIMESTAMP_FORMAT) > time
                self.assertTrue(after_start & before_end)
                # self.assertGreater(time, start_time.strftime(TIMESTAMP_FORMAT), "Event logged before test started")
                # self.assertGreater(end_time.strftime(TIMESTAMP_FORMAT), time, "Event logged after test ended")
