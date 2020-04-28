"""
Provides tests around the Asynchronous Express workflow, including sync-async wrapping
"""
import json
import unittest

from fhir.resources.fhirreference import FHIRReference
from fhir.resources.identifier import Identifier
from fhir.resources.organization import Organization
from fhir.resources.patient import Patient
from fhir.resources.practitioner import Practitioner

from comms.blocking_queue_adaptor import BlockingQueueAdaptor
from outbound.tests.outbound_request_builder import OutboundRequestBuilder
from utilities import config


class NhaisIntegrationTests(unittest.TestCase):
    """
     These tests demonstrate each outbound (GP -> HA) transaction without HA replies
    """

    def setUp(self):
        # TODO: how to we specify the queue name?!? Need to wait for another merge
        config.setup_config('NHAIS')
        self.mq_wrapper = BlockingQueueAdaptor(username=config.get_config('OUTBOUND_QUEUE_USERNAME', default=None),
                                                 password=config.get_config('OUTBOUND_QUEUE_PASSWORD', default=None),
                                                 queue_url=config.get_config('OUTBOUND_QUEUE_HOST'),
                                                 queue_name='mesh_outbound')
        self.mq_wrapper.drain()

# {
#     "id": "254406A3",
#     "type": "Organization",
#     "reference": "https://directory.spineservices.nhs.uk/STU3/Organization/Y12345",
#     "identifier": {
#         "system": "https://digital.nhs.uk/services/organisation-data-service",
#         "value": "Y12345",
#         "period": {
#             "start": "2020-01-01",
#             "end": "2021-12-31"
#         }
#     }
# }

    @staticmethod
    def create_org_ref(id):
        ref = FHIRReference()
        # ref.id = id
        ref.type = "Organisation"
        identifier = Identifier()
        identifier.value = id
        ref.identifier = identifier
        return ref


    @staticmethod
    def create_patient() -> Patient:
        patient = Patient()
        patient.id = '123'
        patient.generalPractitioner = [NhaisIntegrationTests.create_org_ref('GP123')]
        patient.managingOrganization = NhaisIntegrationTests.create_org_ref('HA456')
        return patient

    def test_acceptance_transaction(self):
        patient = self.create_patient()
        response = OutboundRequestBuilder()\
            .with_headers()\
            .with_acceptance_patient(patient)\
            .execute_post_expecting_success()
        message = self.mq_wrapper.get_next_message_on_queue()
        self.assertIsNotNone(message, 'message from queue should exist')
        self.assertTrue(len(message.body) > 0, 'message from queue should not be empty')
        print(message.body)
        # TODO: verify EDIFACT message



