"""
Provides tests around the Asynchronous Express workflow, including sync-async wrapping
"""
import json
import unittest
import uuid

from fhir.resources.fhirreference import FHIRReference
from fhir.resources.identifier import Identifier
from fhir.resources.organization import Organization
from fhir.resources.patient import Patient
from fhir.resources.practitioner import Practitioner

from comms.blocking_queue_adaptor import BlockingQueueAdaptor
from outbound.tests.fhir_test_helpers import create_patient, PATIENT_ID, GP_ID, HA_ID
from outbound.tests.outbound_request_builder import OutboundRequestBuilder
from utilities import config


class NhaisIntegrationTests(unittest.TestCase):
    """
     These tests demonstrate each outbound (GP -> HA) transaction without HA replies
    """

    def setUp(self):
        # TODO: how to we specify the queue name from config once NIAD-170 is merged
        config.setup_config('NHAIS')
        self.mq_wrapper = BlockingQueueAdaptor(username=config.get_config('OUTBOUND_QUEUE_USERNAME', default=None),
                                                 password=config.get_config('OUTBOUND_QUEUE_PASSWORD', default=None),
                                                 queue_url=config.get_config('OUTBOUND_QUEUE_HOST'),
                                                 queue_name='mesh_outbound')
        self.mq_wrapper.drain()

    def test_acceptance_transaction(self):
        patient = create_patient()
        response = OutboundRequestBuilder()\
            .with_headers()\
            .with_acceptance_patient(patient)\
            .execute_post_expecting_success()
        # TODO: assert response once NIAD-170 is merged
        # self.assertIn('operationid', response.headers)
        # try:
        #     uuid.UUID(response.headers['operationid'])  # throws Type
        # except ValueError:
        #     self.fail('operationid header is not a UUID')

        message = self.mq_wrapper.get_next_message_on_queue()
        self.assertIsNotNone(message, 'message from queue should exist')
        body_string = message.body.decode()
        self.assertTrue(len(body_string) > 0, 'message from queue should not be empty')
        self.assertIn(PATIENT_ID, body_string)
        self.assertIn(GP_ID, body_string)
        self.assertIn(HA_ID, body_string)
        # TODO: verify EDIFACT message once inbound parsing work progresses



