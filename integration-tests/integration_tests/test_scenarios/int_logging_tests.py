import datetime

from unittest import skip, TestCase

from integration_tests.helpers import message_retriever, methods, logs_retriever

TIMESTAMP_FORMAT = "%Y-%m-%dT%H:%M:%S.%f"


class FunctionalTest(TestCase):

    @skip("RT-77 work in progress")
    def test_logging_file(self):
        # start the clock
        start_time = datetime.datetime.utcnow()
        print('Time test started: ', start_time.strftime(TIMESTAMP_FORMAT))

        # fire off an (MHS) action that will generate a log file
        methods.get_interaction_from_template('async express',
                                              'QUPC_IN160101UK05',
                                              '9689174746',
                                              'Asynchronous Express test')
        # then retrieve the response from the queue...
        _, _, inbound_response = message_retriever.get_inbound_response()

        # stop the clock
        end_time = datetime.datetime.utcnow()
        print('Time test ended: ', end_time.strftime(TIMESTAMP_FORMAT))

        # get the log file
        logs = logs_retriever.get_logs(logs_retriever.Component.MHS)

        # check the timestamps in the log file are between the start & end times
        for line in logs:
            # extract the timestamp from the line...
            time = methods.get_log_timestamp(line)

            after_start = time > start_time.strftime(TIMESTAMP_FORMAT)
            before_end = end_time.strftime(TIMESTAMP_FORMAT) > time
            self.assertTrue(after_start and before_end)
