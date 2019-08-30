import datetime
import logging
import os
import sys

from unittest import skip, TestCase

from integration_tests.helpers import message_retriever, methods, logs_retriever
from utilities import integration_adaptors_logger as log
from test_definitions import ROOT_DIR


TIMESTAMP_FORMAT = "%Y-%m-%dT%H:%M:%S.%f"


class FunctionalTest(TestCase):

    # This test will read the 'mhs.log' file and check ALL the entries were created by this test
    # When running locally, the log file needs to be deleted first, otherwise the test will fail
    #   due to the previous log entries being out of date...
    def test_logging_file(self):
        # start the clock
        start_time = datetime.datetime.utcnow()
        log_filename = os.path.join(ROOT_DIR, 'mhs.log')

        log.configure_logging([logging.FileHandler(log_filename), logging.StreamHandler(sys.stdout)])
        logs_retriever._component_log_filename_map[logs_retriever.Component.MHS] = log_filename

        # fire off an (MHS) action that will generate a log file
        methods.get_interaction_from_template('async express',
                                              'QUPC_IN160101UK05',
                                              '9689174746',
                                              'Asynchronous Express test')
        # then retrieve the response from the queue...
        _, _, inbound_response = message_retriever.get_inbound_response()

        # stop the clock
        end_time = datetime.datetime.utcnow()

        # get the log file
        logs = logs_retriever.get_logs(logs_retriever.Component.MHS)

        # check the timestamps in the log file are between the start & end times
        for line in logs:
            # extract the timestamp from the line...
            time = methods.get_log_timestamp(line)
            after_start = time > start_time.strftime(TIMESTAMP_FORMAT)
            before_end = end_time.strftime(TIMESTAMP_FORMAT) > time
            self.assertTrue(after_start and before_end)
