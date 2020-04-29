import json
import unittest
import uuid

from fhir.resources.fhirelementfactory import FHIRElementFactory

from comms.blocking_queue_adaptor import BlockingQueueAdaptor
from outbound.tests.fhir_test_helpers import create_patient, GP_ID, HA_ID
from outbound.tests.outbound_request_builder import OutboundRequestBuilder
from utilities import config


class NhaisIntegrationTests(unittest.TestCase):
    """
     These tests demonstrate each outbound (GP -> HA) transaction without HA replies
    """

    def setUp(self):
        config.setup_config('NHAIS')
        self.mq_wrapper = BlockingQueueAdaptor(username=config.get_config('OUTBOUND_QUEUE_USERNAME', default=None),
                                               password=config.get_config('OUTBOUND_QUEUE_PASSWORD', default=None),
                                               queue_url=config.get_config('OUTBOUND_QUEUE_BROKERS'),
                                               queue_name=config.get_config('OUTBOUND_QUEUE_NAME'))
        self.mq_wrapper.drain()

    def test_acceptance_transaction(self):
        patient = create_patient()
        response = OutboundRequestBuilder()\
            .with_headers()\
            .with_acceptance_patient(patient)\
            .execute_post_expecting_success()
        self.assertIn('operationid', response.headers)
        try:
            uuid.UUID(response.headers['operationid'])
        except ValueError:
            self.fail('operationid header is not a UUID')

        message = self.mq_wrapper.get_next_message_on_queue()
        self.assertIsNotNone(message, 'message from queue should exist')
        self.assertTrue(len(message.body) > 0, 'message from queue should not be empty')
        self.assertIn(GP_ID, message.body)
        self.assertIn(HA_ID, message.body)
        # TODO: verify EDIFACT message once inbound parsing work progresses

    def test_acceptance_transaction_translation_error(self):
        patient = create_patient()
        patient.managingOrganization.identifier.value = None

        response = OutboundRequestBuilder() \
            .with_headers() \
            .with_acceptance_patient(patient) \
            .execute_post_expecting_bad_request_response()

        operation_outcome = FHIRElementFactory.instantiate('OperationOutcome', json.loads(response.content.decode()))

        self.assertEqual('error', operation_outcome.issue[0].severity)
        self.assertEqual('', operation_outcome.issue[0].expression[0])
        self.assertEqual('UNB: Attribute recipient is required', operation_outcome.issue[0].details.text)
        self.assertEqual(400, response.status_code)
