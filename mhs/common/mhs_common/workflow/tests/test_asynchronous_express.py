import asyncio
import unittest
from unittest import mock

import exceptions
from comms import proton_queue_adaptor
from tornado import httpclient
from utilities import test_utilities
from utilities.test_utilities import async_test

import mhs_common.workflow.asynchronous_express as async_express
from mhs_common import workflow
from mhs_common.messages import ebxml_request_envelope, ebxml_envelope
from mhs_common.state import work_description
from mhs_common.state.work_description import MessageStatus

FROM_PARTY_KEY = 'from-party-key'
TO_PARTY_KEY = 'to-party-key'
CPA_ID = 'cpa-id'
ASID = 'asid-123'
MESSAGE_ID = 'message-id'
CORRELATION_ID = 'correlation-id'
URL = 'a.a'
ASID = '123456'
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
    'action': ACTION,
    'uniqueIdentifier': "31312"
}
PAYLOAD = 'payload'
SERIALIZED_MESSAGE = 'serialized-message'
INBOUND_QUEUE_MAX_RETRIES = 3
INBOUND_QUEUE_RETRY_DELAY = 100
INBOUND_QUEUE_RETRY_DELAY_IN_SECONDS = INBOUND_QUEUE_RETRY_DELAY / 1000

MHS_END_POINT_KEY = 'nhsMHSEndPoint'
MHS_TO_PARTY_KEY_KEY = 'nhsMHSPartyKey'
MHS_CPA_ID_KEY = 'nhsMhsCPAId'
MHS_ASID = 'uniqueIdentifier'


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
                                                                  inbound_queue_max_retries=INBOUND_QUEUE_MAX_RETRIES,
                                                                  inbound_queue_retry_delay=INBOUND_QUEUE_RETRY_DELAY,
                                                                  persistence_store_max_retries=3,
                                                                  routing=self.mock_routing_reliability)

    def test_construct_workflow_with_only_outbound_params(self):
        workflow = async_express.AsynchronousExpressWorkflow(party_key=mock.sentinel.party_key,
                                                             persistence_store=mock.sentinel.persistence_store,
                                                             transmission=mock.sentinel.transmission,
                                                             routing=self.mock_routing_reliability)
        self.assertIsNotNone(workflow)

    def test_construct_workflow_with_only_inbound_params(self):
        workflow = async_express.AsynchronousExpressWorkflow(queue_adaptor=mock.sentinel.queue_adaptor,
                                                             inbound_queue_max_retries=INBOUND_QUEUE_MAX_RETRIES,
                                                             inbound_queue_retry_delay=INBOUND_QUEUE_RETRY_DELAY)
        self.assertIsNotNone(workflow)
        self.assertEqual(INBOUND_QUEUE_RETRY_DELAY_IN_SECONDS, workflow.inbound_queue_retry_delay)

    ############################
    # Outbound tests
    ############################

    @mock.patch.object(async_express, 'logger')
    @async_test
    async def test_handle_outbound_message(self, log_mock):
        response = mock.MagicMock()
        response.code = 202

        self.setup_mock_work_description()

        self._setup_routing_mock()
        self.mock_ebxml_request_envelope.return_value.serialize.return_value = (
            MESSAGE_ID, HTTP_HEADERS, SERIALIZED_MESSAGE)
        self.mock_transmission_adaptor.make_request.return_value = test_utilities.awaitable(response)

        expected_interaction_details = {ebxml_envelope.MESSAGE_ID: MESSAGE_ID, ebxml_request_envelope.MESSAGE: PAYLOAD,
                                        ebxml_envelope.FROM_PARTY_ID: FROM_PARTY_KEY,
                                        ebxml_envelope.CONVERSATION_ID: CORRELATION_ID,
                                        ebxml_envelope.TO_PARTY_ID: TO_PARTY_KEY,
                                        ebxml_envelope.CPA_ID: CPA_ID}
        expected_interaction_details.update(INTERACTION_DETAILS)

        status, message, _ = await self.workflow.handle_outbound_message(None,
                                                                         MESSAGE_ID,
                                                                         CORRELATION_ID,
                                                                         INTERACTION_DETAILS,
                                                                         PAYLOAD,
                                                                         None)

        self.assertEqual(202, status)
        self.assertEqual('', message)
        self.mock_create_new_work_description.assert_called_once_with(self.mock_persistence_store, MESSAGE_ID,
                                                                      workflow.ASYNC_EXPRESS,
                                                                      MessageStatus.OUTBOUND_MESSAGE_RECEIVED)
        self.mock_work_description.publish.assert_called_once()
        self.assertEqual(
            [mock.call(MessageStatus.OUTBOUND_MESSAGE_PREPARED), mock.call(MessageStatus.OUTBOUND_MESSAGE_ACKD)],
            self.mock_work_description.set_outbound_status.call_args_list)
        self.mock_routing_reliability.get_end_point.assert_called_once_with(SERVICE_ID)
        self.mock_ebxml_request_envelope.assert_called_once_with(expected_interaction_details)
        self.mock_transmission_adaptor.make_request.assert_called_once_with(URL, HTTP_HEADERS, SERIALIZED_MESSAGE)
        self.assert_audit_log_recorded_with_message_status(log_mock, MessageStatus.OUTBOUND_MESSAGE_ACKD)

    @mock.patch('mhs_common.state.work_description.create_new_work_description')
    @mock.patch.object(async_express, 'logger')
    @async_test
    async def test_handle_outbound_doesnt_overwrite_work_description(self, log_mock, wdo_mock):
        response = mock.MagicMock()
        response.code = 202

        self.setup_mock_work_description()

        self._setup_routing_mock()
        self.mock_ebxml_request_envelope.return_value.serialize.return_value = (
            MESSAGE_ID, HTTP_HEADERS, SERIALIZED_MESSAGE)
        self.mock_transmission_adaptor.make_request.return_value = test_utilities.awaitable(response)

        expected_interaction_details = {ebxml_envelope.MESSAGE_ID: MESSAGE_ID, ebxml_request_envelope.MESSAGE: PAYLOAD,
                                        ebxml_envelope.FROM_PARTY_ID: FROM_PARTY_KEY,
                                        ebxml_envelope.CONVERSATION_ID: CORRELATION_ID,
                                        ebxml_envelope.TO_PARTY_ID: TO_PARTY_KEY,
                                        ebxml_envelope.CPA_ID: CPA_ID}
        expected_interaction_details.update(INTERACTION_DETAILS)

        wdo = mock.MagicMock()
        wdo.workflow = 'This should not change'
        wdo.set_outbound_status.return_value = test_utilities.awaitable(True)
        wdo.update.return_value = test_utilities.awaitable(True)
        status, message, _ = await self.workflow.handle_outbound_message(None, MESSAGE_ID, CORRELATION_ID,
                                                                         INTERACTION_DETAILS,
                                                                         PAYLOAD, wdo)

        self.assertEqual(202, status)
        wdo_mock.assert_not_called()
        self.assertEqual(wdo.workflow, 'This should not change')

    @async_test
    async def test_handle_outbound_message_serialisation_fails(self):
        self.setup_mock_work_description()
        self._setup_routing_mock()

        self.mock_ebxml_request_envelope.return_value.serialize.side_effect = Exception()

        status, message, _ = await self.workflow.handle_outbound_message(None, MESSAGE_ID, CORRELATION_ID,
                                                                         INTERACTION_DETAILS,
                                                                         PAYLOAD, None)

        self.assertEqual(500, status)
        self.assertEqual('Error serialising outbound message', message)
        self.mock_work_description.publish.assert_called_once()
        self.assertEqual([mock.call(MessageStatus.OUTBOUND_MESSAGE_PREPARATION_FAILED)],
                         self.mock_work_description.set_outbound_status.call_args_list)
        self.mock_transmission_adaptor.make_request.assert_not_called()

    @async_test
    async def test_handle_outbound_message_error_when_looking_up_url(self):
        self.setup_mock_work_description()
        self.mock_routing_reliability.get_end_point.side_effect = Exception()

        status, message, _ = await self.workflow.handle_outbound_message(None, MESSAGE_ID, CORRELATION_ID,
                                                                         INTERACTION_DETAILS,
                                                                         PAYLOAD, None)

        self.assertEqual(500, status)
        self.assertEqual('Error obtaining outbound URL', message)
        self.mock_work_description.publish.assert_called_once()
        self.assertEqual([mock.call(MessageStatus.OUTBOUND_MESSAGE_TRANSMISSION_FAILED)],
                         self.mock_work_description.set_outbound_status.call_args_list)
        self.mock_transmission_adaptor.make_request.assert_not_called()

    @mock.patch.object(async_express, 'logger')
    @async_test
    async def test_handle_outbound_message_http_error_when_calling_outbound_transmission(self, log_mock):
        self.setup_mock_work_description()
        self._setup_routing_mock()

        self.mock_ebxml_request_envelope.return_value.serialize.return_value = (MESSAGE_ID, {}, SERIALIZED_MESSAGE)

        future = asyncio.Future()
        future.set_exception(httpclient.HTTPClientError(code=409))
        self.mock_transmission_adaptor.make_request.return_value = future

        status, message, _ = await self.workflow.handle_outbound_message(None, MESSAGE_ID, CORRELATION_ID,
                                                                         INTERACTION_DETAILS,
                                                                         PAYLOAD, None)

        self.assertEqual(500, status)
        self.assertTrue('Error(s) received from Spine' in message)
        self.mock_work_description.publish.assert_called_once()
        self.assertEqual(
            [mock.call(MessageStatus.OUTBOUND_MESSAGE_PREPARED), mock.call(MessageStatus.OUTBOUND_MESSAGE_NACKD)],
            self.mock_work_description.set_outbound_status.call_args_list)
        self.assert_audit_log_recorded_with_message_status(log_mock, MessageStatus.OUTBOUND_MESSAGE_NACKD)

    @async_test
    async def test_handle_outbound_message_error_when_calling_outbound_transmission(self):
        self.setup_mock_work_description()
        self._setup_routing_mock()

        self.mock_ebxml_request_envelope.return_value.serialize.return_value = (MESSAGE_ID, {}, SERIALIZED_MESSAGE)

        future = asyncio.Future()
        future.set_exception(Exception())
        self.mock_transmission_adaptor.make_request.return_value = future

        status, message, _ = await self.workflow.handle_outbound_message(None, MESSAGE_ID, CORRELATION_ID,
                                                                         INTERACTION_DETAILS,
                                                                         PAYLOAD, None)

        self.assertEqual(500, status)
        self.assertEqual('Error making outbound request', message)
        self.mock_work_description.publish.assert_called_once()
        self.assertEqual(
            [mock.call(MessageStatus.OUTBOUND_MESSAGE_PREPARED),
             mock.call(MessageStatus.OUTBOUND_MESSAGE_TRANSMISSION_FAILED)],
            self.mock_work_description.set_outbound_status.call_args_list)

    @mock.patch.object(async_express, 'logger')
    @async_test
    async def test_handle_outbound_message_non_http_202_success_response_received(self, log_mock):
        self.setup_mock_work_description()
        self._setup_routing_mock()

        self.mock_ebxml_request_envelope.return_value.serialize.return_value = (MESSAGE_ID, {}, SERIALIZED_MESSAGE)

        response = mock.MagicMock()
        response.code = 200
        response.headers = {'Content-Type': 'text/xml'}
        response.body = '<a></a>'
        self.mock_transmission_adaptor.make_request.return_value = test_utilities.awaitable(response)

        status, message, _ = await self.workflow.handle_outbound_message(None, MESSAGE_ID, CORRELATION_ID,
                                                                         INTERACTION_DETAILS,
                                                                         PAYLOAD, None)

        self.assertEqual(500, status)
        self.assertEqual("Didn't get expected success response from Spine", message)
        self.mock_work_description.publish.assert_called_once()
        self.assertEqual(
            [mock.call(MessageStatus.OUTBOUND_MESSAGE_PREPARED), mock.call(MessageStatus.OUTBOUND_MESSAGE_NACKD)],
            self.mock_work_description.set_outbound_status.call_args_list)
        self.assert_audit_log_recorded_with_message_status(log_mock, MessageStatus.OUTBOUND_MESSAGE_NACKD)

    @async_test
    async def test_handle_outbound_message_non_http_202_success_response_ebxml_error(self):
        self.setup_mock_work_description()
        self._setup_routing_mock()

        self.mock_ebxml_request_envelope.return_value.serialize.return_value = (MESSAGE_ID, {}, SERIALIZED_MESSAGE)

        response = mock.MagicMock()
        response.code = 200
        response.headers = {'Content-Type': 'text/xml'}
        response.body = """<?xml version="1.0" encoding="utf-8"?>
        <SOAP:Envelope xmlns:SOAP="http://schemas.xmlsoap.org/soap/envelope/" xmlns:eb="http://www.oasis-open.org/committees/ebxml-msg/schema/msg-header-2_0.xsd">
            <SOAP:Header>
                <eb:MessageHeader SOAP:mustUnderstand="1" eb:version="2.0">
                    <eb:From>
                        <eb:PartyId eb:type="urn:nhs:names:partyType:ocs+serviceInstance">YEA-801248</eb:PartyId>
                    </eb:From>
                    <eb:To>
                        <eb:PartyId eb:type="urn:nhs:names:partyType:ocs+serviceInstance">RHM-810292</eb:PartyId>
                    </eb:To>
                    <eb:CPAId>S2001919A2011852</eb:CPAId>
                    <eb:ConversationId>19D02203-3CBE-11E3-9D44-9D223D2F4DB0</eb:ConversationId>
                    <eb:Service>urn:oasis:names:tc:ebxml-msg:service</eb:Service>
                    <eb:Action>MessageError</eb:Action>
                    <eb:MessageData>
                        <eb:MessageId>97111C1C-48B8-B2FA-DE13-B64B2ADEB391</eb:MessageId>
                        <eb:Timestamp>2013-10-24T15:08:07</eb:Timestamp>
                        <eb:RefToMessageId>19D02203-3CBE-11E3-9D44-9D223D2F4DB0</eb:RefToMessageId>
                    </eb:MessageData>
                </eb:MessageHeader>
                <eb:ErrorList SOAP:mustUnderstand="1" eb:highestSeverity="Error" eb:version="2.0">
                    <eb:Error eb:codeContext="urn:oasis:names:tc:ebxml-msg:service:errors" eb:errorCode="ValueNotRecognized" eb:severity="Error">
                        <eb:Description xml:lang="en-GB">501319:Unknown eb:CPAId</eb:Description>
                    </eb:Error>
                </eb:ErrorList>
            </SOAP:Header>
            <SOAP:Body/>
        </SOAP:Envelope>
        """
        self.mock_transmission_adaptor.make_request.return_value = test_utilities.awaitable(response)

        status, message = await self.workflow.handle_outbound_message(MESSAGE_ID, CORRELATION_ID, INTERACTION_DETAILS,
                                                                      PAYLOAD, None)

        self.assertEqual(500, status)
        self.assertIn("Error(s) received from Spine. Contact system administrator", message)
        self.mock_work_description.publish.assert_called_once()
        self.assertEqual(
            [mock.call(MessageStatus.OUTBOUND_MESSAGE_PREPARED), mock.call(MessageStatus.OUTBOUND_MESSAGE_TRANSMISSION_FAILED)],
            self.mock_work_description.set_outbound_status.call_args_list)

    def _setup_routing_mock(self):
        self.mock_routing_reliability.get_end_point.return_value = test_utilities.awaitable({
            MHS_END_POINT_KEY: [URL],
            MHS_TO_PARTY_KEY_KEY: TO_PARTY_KEY,
            MHS_CPA_ID_KEY: CPA_ID,
            MHS_ASID: [ASID]
        })

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
                         self.mock_work_description.set_inbound_status.call_args_list)

    @mock.patch('asyncio.sleep')
    @async_test
    async def test_handle_inbound_message_error_putting_message_onto_queue_then_success(self, mock_sleep):
        self.setup_mock_work_description()
        error_future = asyncio.Future()
        error_future.set_exception(proton_queue_adaptor.MessageSendingError())
        self.mock_queue_adaptor.send_async.side_effect = [error_future, test_utilities.awaitable(None)]
        mock_sleep.return_value = test_utilities.awaitable(None)

        await self.workflow.handle_inbound_message(MESSAGE_ID, CORRELATION_ID, self.mock_work_description, PAYLOAD)

        self.mock_queue_adaptor.send_async.assert_called_with(PAYLOAD,
                                                              properties={'message-id': MESSAGE_ID,
                                                                          'correlation-id': CORRELATION_ID})
        self.assertEqual([mock.call(MessageStatus.INBOUND_RESPONSE_RECEIVED),
                          mock.call(MessageStatus.INBOUND_RESPONSE_SUCCESSFULLY_PROCESSED)],
                         self.mock_work_description.set_inbound_status.call_args_list)
        mock_sleep.assert_called_once_with(INBOUND_QUEUE_RETRY_DELAY_IN_SECONDS)

    @mock.patch('asyncio.sleep')
    @async_test
    async def test_handle_inbound_message_error_putting_message_onto_queue_despite_retries(self, mock_sleep):
        self.setup_mock_work_description()
        future = asyncio.Future()
        future.set_exception(proton_queue_adaptor.MessageSendingError())
        self.mock_queue_adaptor.send_async.return_value = future
        mock_sleep.return_value = test_utilities.awaitable(None)

        with self.assertRaises(exceptions.MaxRetriesExceeded) as cm:
            await self.workflow.handle_inbound_message(MESSAGE_ID, CORRELATION_ID, self.mock_work_description, PAYLOAD)
        self.assertIsInstance(cm.exception.__cause__, proton_queue_adaptor.MessageSendingError)

        self.assertEqual(
            [mock.call(INBOUND_QUEUE_RETRY_DELAY_IN_SECONDS) for _ in range(INBOUND_QUEUE_MAX_RETRIES - 1)],
            mock_sleep.call_args_list)

        self.assertEqual([mock.call(MessageStatus.INBOUND_RESPONSE_RECEIVED),
                          mock.call(MessageStatus.INBOUND_RESPONSE_FAILED)],
                         self.mock_work_description.set_inbound_status.call_args_list)

    def setup_mock_work_description(self):
        self.mock_work_description = self.mock_create_new_work_description.return_value
        self.mock_work_description.publish.return_value = test_utilities.awaitable(None)
        self.mock_work_description.set_outbound_status.return_value = test_utilities.awaitable(None)
        self.mock_work_description.set_inbound_status.return_value = test_utilities.awaitable(None)
        self.mock_work_description.update.return_value = test_utilities.awaitable(None)

    def assert_audit_log_recorded_with_message_status(self, log_mock, message_status):
        log_mock.audit.assert_called_once()
        audit_log_dict = log_mock.audit.call_args[0][2]
        self.assertEqual(message_status, audit_log_dict['Acknowledgment'])
