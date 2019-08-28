import asyncio
import unittest
from unittest import mock

from comms import proton_queue_adaptor
from tornado import httpclient
from utilities import test_utilities, config
from utilities.test_utilities import async_test

import mhs_common.workflow.asynchronous_express as async_express
from mhs_common import workflow
from mhs_common.messages import ebxml_request_envelope, ebxml_envelope
from mhs_common.state import work_description
from mhs_common.state.work_description import MessageStatus

FROM_PARTY_KEY = 'to-party-key'
TO_PARTY_KEY = 'from-party-key'
MESSAGE_ID = 'message-id'
CORRELATION_ID = 'correlation-id'
CPA_ID = 'cpa-id'
URL = 'a.a'
HTTP_HEADERS = {
    "type": "a",
    "Content-Type": "b",
    "charset": "c",
    "SOAPAction": "d",
    'start': "e"
}
SERVICE = 'service'
ACTION = 'action'
SERVICE_ID = SERVICE + ":" + ACTION
INTERACTION_DETAILS = {
    'workflow': 'async-express',
    'service': SERVICE,
    'action': ACTION
}
PAYLOAD = 'payload'
SERIALIZED_MESSAGE = 'serialized-message'
SPINE_ORG_CODE_CONFIG_KEY = 'SPINE_ORG_CODE'
SPINE_ORG_CODE = "spine-org-code"


class TestAsynchronousExpressWorkflow(unittest.TestCase):
    def setUp(self):
        self.mock_persistence_store = mock.MagicMock()
        self.mock_transmission_adaptor = mock.MagicMock()
        self.mock_queue_adaptor = mock.MagicMock()
        self.mock_routing_reliability = mock.MagicMock()

        patcher = mock.patch.object(work_description, 'create_new_work_description')
        self.mock_create_new_work_description = patcher.start()
        self.addCleanup(patcher.stop)

        patcher = mock.patch.object(ebxml_request_envelope, 'EbxmlRequestEnvelope')
        self.mock_ebxml_request_envelope = patcher.start()
        self.addCleanup(patcher.stop)

        self.workflow = async_express.AsynchronousExpressWorkflow(party_key=FROM_PARTY_KEY,
                                                                  persistence_store=self.mock_persistence_store,
                                                                  transmission=self.mock_transmission_adaptor,
                                                                  queue_adaptor=self.mock_queue_adaptor,
                                                                  routing_reliability=self.mock_routing_reliability)

    ############################
    # Outbound tests
    ############################

    @mock.patch.object(async_express, 'logger')
    @async_test
    async def test_handle_outbound_message(self, log_mock):
        response = mock.MagicMock()
        response.code = 202

        self.setup_mock_work_description()

        self._setup_routing_mocks()
        self.mock_ebxml_request_envelope.return_value.serialize.return_value = (
            MESSAGE_ID, HTTP_HEADERS, SERIALIZED_MESSAGE)
        self.mock_transmission_adaptor.make_request.return_value = test_utilities.awaitable(response)

        expected_interaction_details = {ebxml_envelope.MESSAGE_ID: MESSAGE_ID, ebxml_request_envelope.MESSAGE: PAYLOAD,
                                        ebxml_envelope.FROM_PARTY_ID: FROM_PARTY_KEY,
                                        ebxml_envelope.CONVERSATION_ID: CORRELATION_ID, ebxml_envelope.CPA_ID: CPA_ID,
                                        ebxml_envelope.TO_PARTY_ID: TO_PARTY_KEY}
        expected_interaction_details.update(INTERACTION_DETAILS)

        status, message = await self.workflow.handle_outbound_message(MESSAGE_ID, CORRELATION_ID, INTERACTION_DETAILS,
                                                                      PAYLOAD)

        self.assertEqual(202, status)
        self.assertEqual('', message)
        self.mock_create_new_work_description.assert_called_once_with(self.mock_persistence_store, MESSAGE_ID,
                                                                      MessageStatus.OUTBOUND_MESSAGE_RECEIVED,
                                                                      workflow.ASYNC_EXPRESS)
        self.mock_work_description.publish.assert_called_once()
        self.assertEqual(
            [mock.call(MessageStatus.OUTBOUND_MESSAGE_PREPARED), mock.call(MessageStatus.OUTBOUND_MESSAGE_ACKD)],
            self.mock_work_description.set_status.call_args_list)
        self.mock_routing_reliability.get_end_point.assert_called_once_with(SPINE_ORG_CODE, SERVICE_ID)
        self.mock_ebxml_request_envelope.assert_called_once_with(expected_interaction_details)
        self.mock_transmission_adaptor.make_request.assert_called_once_with(URL, HTTP_HEADERS, SERIALIZED_MESSAGE)
        self.assert_audit_log_recorded_with_message_status(log_mock, MessageStatus.OUTBOUND_MESSAGE_ACKD)

    @async_test
    async def test_handle_outbound_message_serialisation_fails(self):
        self.setup_mock_work_description()
        self._setup_routing_mocks()

        self.mock_ebxml_request_envelope.return_value.serialize.side_effect = Exception()

        status, message = await self.workflow.handle_outbound_message(MESSAGE_ID, CORRELATION_ID, INTERACTION_DETAILS,
                                                                      PAYLOAD)

        self.assertEqual(500, status)
        self.assertEqual('Error serialising outbound message', message)
        self.mock_work_description.publish.assert_called_once()
        self.assertEqual([mock.call(MessageStatus.OUTBOUND_MESSAGE_PREPARATION_FAILED)],
                         self.mock_work_description.set_status.call_args_list)
        self.mock_transmission_adaptor.make_request.assert_not_called()

    @async_test
    async def test_handle_outbound_message_error_when_looking_up_url(self):
        self.setup_mock_work_description()
        self.mock_routing_reliability.get_end_point.side_effect = Exception()

        status, message = await self.workflow.handle_outbound_message(MESSAGE_ID, CORRELATION_ID, INTERACTION_DETAILS,
                                                                      PAYLOAD)

        self.assertEqual(500, status)
        self.assertEqual('Error obtaining outbound URL', message)
        self.mock_work_description.publish.assert_called_once()
        self.assertEqual([mock.call(MessageStatus.OUTBOUND_MESSAGE_TRANSMISSION_FAILED)],
                         self.mock_work_description.set_status.call_args_list)
        self.mock_transmission_adaptor.make_request.assert_not_called()

    @mock.patch.object(async_express, 'logger')
    @async_test
    async def test_handle_outbound_message_http_error_when_calling_outbound_transmission(self, log_mock):
        self.setup_mock_work_description()
        self._setup_routing_mocks()

        self.mock_ebxml_request_envelope.return_value.serialize.return_value = (MESSAGE_ID, {}, SERIALIZED_MESSAGE)

        future = asyncio.Future()
        future.set_exception(httpclient.HTTPClientError(code=409))
        self.mock_transmission_adaptor.make_request.return_value = future

        status, message = await self.workflow.handle_outbound_message(MESSAGE_ID, CORRELATION_ID, INTERACTION_DETAILS,
                                                                      PAYLOAD)

        self.assertEqual(500, status)
        self.assertEqual('Error received from Spine', message)
        self.mock_work_description.publish.assert_called_once()
        self.assertEqual(
            [mock.call(MessageStatus.OUTBOUND_MESSAGE_PREPARED), mock.call(MessageStatus.OUTBOUND_MESSAGE_NACKD)],
            self.mock_work_description.set_status.call_args_list)
        self.assert_audit_log_recorded_with_message_status(log_mock, MessageStatus.OUTBOUND_MESSAGE_NACKD)

    @async_test
    async def test_handle_outbound_message_error_when_calling_outbound_transmission(self):
        self.setup_mock_work_description()
        self._setup_routing_mocks()

        self.mock_ebxml_request_envelope.return_value.serialize.return_value = (MESSAGE_ID, {}, SERIALIZED_MESSAGE)

        future = asyncio.Future()
        future.set_exception(Exception())
        self.mock_transmission_adaptor.make_request.return_value = future

        status, message = await self.workflow.handle_outbound_message(MESSAGE_ID, CORRELATION_ID, INTERACTION_DETAILS,
                                                                      PAYLOAD)

        self.assertEqual(500, status)
        self.assertEqual('Error making outbound request', message)
        self.mock_work_description.publish.assert_called_once()
        self.assertEqual(
            [mock.call(MessageStatus.OUTBOUND_MESSAGE_PREPARED),
             mock.call(MessageStatus.OUTBOUND_MESSAGE_TRANSMISSION_FAILED)],
            self.mock_work_description.set_status.call_args_list)

    @mock.patch.object(async_express, 'logger')
    @async_test
    async def test_handle_outbound_message_non_http_202_success_response_received(self, log_mock):
        self.setup_mock_work_description()
        self._setup_routing_mocks()

        self.mock_ebxml_request_envelope.return_value.serialize.return_value = (MESSAGE_ID, {}, SERIALIZED_MESSAGE)

        response = mock.MagicMock()
        response.code = 200
        self.mock_transmission_adaptor.make_request.return_value = test_utilities.awaitable(response)

        status, message = await self.workflow.handle_outbound_message(MESSAGE_ID, CORRELATION_ID, INTERACTION_DETAILS,
                                                                      PAYLOAD)

        self.assertEqual(500, status)
        self.assertEqual("Didn't get expected success response from Spine", message)
        self.mock_work_description.publish.assert_called_once()
        self.assertEqual(
            [mock.call(MessageStatus.OUTBOUND_MESSAGE_PREPARED), mock.call(MessageStatus.OUTBOUND_MESSAGE_NACKD)],
            self.mock_work_description.set_status.call_args_list)
        self.assert_audit_log_recorded_with_message_status(log_mock, MessageStatus.OUTBOUND_MESSAGE_NACKD)

    def _setup_routing_mocks(self):
        config.config[SPINE_ORG_CODE_CONFIG_KEY] = SPINE_ORG_CODE
        self.mock_routing_reliability.get_end_point.return_value = test_utilities.awaitable({
            'nhsMHSEndPoint': [URL], 'nhsMhsCPAId': CPA_ID, 'nhsMHSPartyKey': TO_PARTY_KEY})

    ############################
    # Inbound tests
    ############################

    @async_test
    async def test_handle_inbound_message(self):
        self.setup_mock_work_description()
        self.mock_queue_adaptor.send_async.return_value = test_utilities.awaitable(None)

        await self.workflow.handle_inbound_message(MESSAGE_ID, CORRELATION_ID, self.mock_work_description, PAYLOAD)

        self.mock_queue_adaptor.send_async.assert_called_once_with(PAYLOAD,
                                                                   properties={'message-id': MESSAGE_ID,
                                                                               'correlation-id': CORRELATION_ID})
        self.assertEqual([mock.call(MessageStatus.INBOUND_RESPONSE_RECEIVED),
                          mock.call(MessageStatus.INBOUND_RESPONSE_SUCCESSFULLY_PROCESSED)],
                         self.mock_work_description.set_status.call_args_list)

    @async_test
    async def test_handle_inbound_message_error_putting_message_onto_queue(self):
        self.setup_mock_work_description()
        future = asyncio.Future()
        future.set_exception(proton_queue_adaptor.MessageSendingError())
        self.mock_queue_adaptor.send_async.return_value = future

        with self.assertRaises(proton_queue_adaptor.MessageSendingError):
            await self.workflow.handle_inbound_message(MESSAGE_ID, CORRELATION_ID, self.mock_work_description, PAYLOAD)

        self.assertEqual([mock.call(MessageStatus.INBOUND_RESPONSE_RECEIVED),
                          mock.call(MessageStatus.INBOUND_RESPONSE_FAILED)],
                         self.mock_work_description.set_status.call_args_list)

    def setup_mock_work_description(self):
        self.mock_work_description = self.mock_create_new_work_description.return_value
        self.mock_work_description.publish.return_value = test_utilities.awaitable(None)
        self.mock_work_description.set_status.return_value = test_utilities.awaitable(None)

    def assert_audit_log_recorded_with_message_status(self, log_mock, message_status):
        log_mock.audit.assert_called_once()
        audit_log_dict = log_mock.audit.call_args[0][2]
        self.assertEqual(message_status, audit_log_dict['Acknowledgment'])
