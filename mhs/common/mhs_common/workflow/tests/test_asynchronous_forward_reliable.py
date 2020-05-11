import asyncio
import json
import ssl
import unittest
from pathlib import Path
from unittest import mock

from tornado import httpclient

import mhs_common.workflow.asynchronous_forward_reliable as forward_reliable
import mhs_common.workflow.common_asynchronous as common_async
import utilities.file_utilities as file_utilities
from comms import proton_queue_adaptor
from definitions import ROOT_DIR
from mhs_common import workflow
from mhs_common.messages import ebxml_request_envelope, ebxml_envelope
from mhs_common.state import work_description
from mhs_common.state.work_description import MessageStatus
from mhs_common.workflow.common import MessageData
from utilities import test_utilities
from utilities.test_utilities import async_test

FROM_PARTY_KEY = 'from-party-key'
TO_PARTY_KEY = 'to-party-key'
CPA_ID = 'cpa-id'
ASID = 'asid-123'
MESSAGE_ID = 'message-id'
CORRELATION_ID = 'correlation-id'
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
ODS_CODE = 'ODS code'
INTERACTION_DETAILS = {
    'workflow': 'forward-reliable',
    'service': SERVICE,
    'action': ACTION,
    'uniqueIdentifier': "31312",
    'ods-code': ODS_CODE
}
EBXML = "ebxml_data"
PAYLOAD = 'payload'
SERIALIZED_MESSAGE = 'serialized-message'
ATTACHMENTS = [{
    ebxml_request_envelope.ATTACHMENT_CONTENT_ID: '8F1D7DE1-02AB-48D7-A797-A947B09F347F@spine.nhs.uk',
    ebxml_request_envelope.ATTACHMENT_CONTENT_TYPE: 'text/plain',
    ebxml_request_envelope.ATTACHMENT_BASE64: False,
    ebxml_request_envelope.ATTACHMENT_DESCRIPTION: 'Some description',
    ebxml_request_envelope.ATTACHMENT_PAYLOAD: 'Some payload'
}]
INBOUND_MESSAGE_DATA = MessageData(EBXML, PAYLOAD, ATTACHMENTS)
MAX_REQUEST_SIZE = 5_000_000
MHS_END_POINT_KEY = 'nhsMHSEndPoint'
MHS_TO_PARTY_KEY_KEY = 'nhsMHSPartyKey'
MHS_CPA_ID_KEY = 'nhsMhsCPAId'
MHS_ASID = 'uniqueIdentifier'
MHS_RETRY_INTERVAL_VAL = 'PT1S'
MHS_RETRY_INTERVAL_VAL_IN_SECONDS = 1
MHS_RETRY_VAL = 3
MHS_RETRY_INTERVAL_INVALID_VAL = 'P'

TEST_MESSAGE_DIR = "mhs_common/messages/tests/test_messages"


class TestForwardReliableWorkflow(unittest.TestCase):
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

        self.workflow = forward_reliable.AsynchronousForwardReliableWorkflow(
            party_key=FROM_PARTY_KEY,
            persistence_store=self.mock_persistence_store,
            transmission=self.mock_transmission_adaptor,
            queue_adaptor=self.mock_queue_adaptor,
            max_request_size=MAX_REQUEST_SIZE,
            routing=self.mock_routing_reliability
        )

        self.test_message_dir = Path(ROOT_DIR) / TEST_MESSAGE_DIR

    def test_construct_workflow_with_only_outbound_params(self):
        workflow = forward_reliable.AsynchronousForwardReliableWorkflow(
            party_key=mock.sentinel.party_key,
            persistence_store=mock.sentinel.persistence_store,
            transmission=mock.sentinel.transmission,
            routing=self.mock_routing_reliability
        )
        self.assertIsNotNone(workflow)

    ############################
    # Outbound tests
    ############################

    @mock.patch('utilities.integration_adaptors_logger.IntegrationAdaptorsLogger.audit')
    @async_test
    async def test_successful_handle_outbound_message(self, audit_log_mock):
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

        mock_url = 'localhost/reliablemessaging/queryrequest'
        with mock.patch('utilities.config.get_config', return_value=mock_url) as mock_get_config:
            status, message, _ = await self.workflow.handle_outbound_message(None, MESSAGE_ID, CORRELATION_ID,
                                                                             INTERACTION_DETAILS,
                                                                             PAYLOAD, None)
            mock_get_config.assert_called_once_with('FORWARD_RELIABLE_ENDPOINT_URL')

        self.assertEqual(202, status)
        self.assertEqual('', message)
        self.mock_create_new_work_description.assert_called_once_with(
            self.mock_persistence_store, MESSAGE_ID,
            workflow.FORWARD_RELIABLE,
            outbound_status=MessageStatus.OUTBOUND_MESSAGE_RECEIVED
        )
        self.mock_work_description.publish.assert_called_once()
        self.assertEqual(
            [mock.call(MessageStatus.OUTBOUND_MESSAGE_ACKD)],
            self.mock_work_description.set_outbound_status.call_args_list)
        self.mock_routing_reliability.get_end_point.assert_called_once_with(SERVICE_ID, ODS_CODE)
        self.mock_ebxml_request_envelope.assert_called_once_with(expected_interaction_details)
        self.mock_transmission_adaptor.make_request.assert_called_once_with(mock_url, HTTP_HEADERS, SERIALIZED_MESSAGE,
                                                                            raise_error_response=False)
        audit_log_mock.assert_called_with('{WorkflowName} outbound workflow invoked. Message sent to Spine'
                                          ' and {Acknowledgment} received.',
                                          fparams={
                                              'Acknowledgment': 'OUTBOUND_MESSAGE_ACKD',
                                              'WorkflowName': 'forward-reliable'
                                          })

    @mock.patch('mhs_common.state.work_description.create_new_work_description')
    @mock.patch('utilities.config.get_config', return_value='localhost/reliablemessaging/queryrequest')
    @async_test
    async def test_handle_outbound_doesnt_overwrite_work_description(self, config_mock, wdo_mock):
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

        with mock.patch('utilities.config.get_config', return_value='localhost/reliablemessaging/queryrequest'):
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
    async def test_handle_outbound_message_fails_with_serialised_message_too_large(self):
        self.setup_mock_work_description()
        self._setup_routing_mock()

        self.mock_ebxml_request_envelope.return_value.serialize.return_value = (
            MESSAGE_ID, HTTP_HEADERS, 'e' * (MAX_REQUEST_SIZE + 1))

        with mock.patch('utilities.config.get_config', return_value='localhost/reliablemessaging/queryrequest'):
            status, message, _ = await self.workflow.handle_outbound_message(None, MESSAGE_ID, CORRELATION_ID,
                                                                             INTERACTION_DETAILS,
                                                                             PAYLOAD, None)

        self.assertEqual(400, status)
        self.assertIn('Request to send to Spine is too large', message)
        self.assertEqual([mock.call(MessageStatus.OUTBOUND_MESSAGE_PREPARATION_FAILED)],
                         self.mock_work_description.set_outbound_status.call_args_list)
        self.mock_transmission_adaptor.make_request.assert_not_called()

    @async_test
    async def test_handle_outbound_message_error_when_looking_up_spine_url(self):
        self.setup_mock_work_description()
        self.mock_routing_reliability.get_end_point.side_effect = Exception()

        status, message, _ = await self.workflow.handle_outbound_message(None, MESSAGE_ID, CORRELATION_ID,
                                                                         INTERACTION_DETAILS,
                                                                         PAYLOAD, None)

        self.assertEqual(500, status)
        self.assertEqual('Error obtaining outbound URL', message)
        self.mock_work_description.publish.assert_called_once()
        self.assertEqual([mock.call(MessageStatus.OUTBOUND_MESSAGE_PREPARATION_FAILED)],
                         self.mock_work_description.set_outbound_status.call_args_list)
        self.mock_transmission_adaptor.make_request.assert_not_called()

    @async_test
    async def test_non_http_error_handled_when_making_request_to_spine(self):
        self.setup_mock_work_description()
        self._setup_routing_mock()

        self.mock_ebxml_request_envelope.return_value.serialize.return_value = (MESSAGE_ID, {}, SERIALIZED_MESSAGE)

        error_future = asyncio.Future()
        error_future.set_exception(ssl.SSLError())
        self.mock_transmission_adaptor.make_request.return_value = error_future

        with mock.patch('utilities.config.get_config', return_value='localhost/reliablemessaging/queryrequest'):
            status, message, _ = await self.workflow.handle_outbound_message(None, MESSAGE_ID, CORRELATION_ID,
                                                                             INTERACTION_DETAILS,
                                                                             PAYLOAD, None)

        self.assertEqual(500, status)
        self.assertEqual("Error making outbound request", message)
        self.mock_work_description.publish.assert_called_once()
        self.assertEqual(
            [mock.call(MessageStatus.OUTBOUND_MESSAGE_TRANSMISSION_FAILED)],
            self.mock_work_description.set_outbound_status.call_args_list)

    @mock.patch('asyncio.sleep')
    @mock.patch('utilities.integration_adaptors_logger.IntegrationAdaptorsLogger.audit')
    @async_test
    async def test_well_formed_soap_error_response_from_spine(self, audit_log_mock, mock_sleep):
        self.setup_mock_work_description()
        self._setup_routing_mock()
        mock_sleep.return_value = test_utilities.awaitable(None)

        self.mock_ebxml_request_envelope.return_value.serialize.return_value = (MESSAGE_ID, {}, SERIALIZED_MESSAGE)

        message = file_utilities.get_file_string(Path(self.test_message_dir) / 'soapfault_response_single_error.xml')

        response = httpclient.HTTPResponse
        response.code = 500
        response.body = message
        response.headers = {'Content-Type': 'text/xml'}

        self.mock_transmission_adaptor.make_request.return_value = test_utilities.awaitable(response)

        with mock.patch('utilities.config.get_config', return_value='localhost/reliablemessaging/queryrequest'):
            status, message, _ = await self.workflow.handle_outbound_message(None, MESSAGE_ID, CORRELATION_ID,
                                                                             INTERACTION_DETAILS,
                                                                             PAYLOAD, None)
        resp_json = json.loads(message)

        self.assertEqual(500, status)
        self.assertEqual(resp_json['error_message'], "Error(s) received from Spine. Contact system administrator.")
        self.assertEqual(resp_json['process_key'], "SOAP_ERROR_HANDLER0002")
        self.assertEqual(resp_json['errors'][0]['codeContext'], "urn:nhs:names:error:tms")
        self.assertEqual(resp_json['errors'][0]['description'], "System failure to process message - default")
        self.assertEqual(resp_json['errors'][0]['errorCode'], "200")
        self.assertEqual(resp_json['errors'][0]['errorType'], "soap_fault")
        self.assertEqual(resp_json['errors'][0]['severity'], "Error")

        self.mock_work_description.publish.assert_called_once()
        self.assertEqual(
            [mock.call(MessageStatus.OUTBOUND_MESSAGE_NACKD)],
            self.mock_work_description.set_outbound_status.call_args_list)
        audit_log_mock.assert_called_once_with('Outbound {WorkflowName} workflow invoked.',
                                               fparams={'WorkflowName': 'forward-reliable'})

    @mock.patch('utilities.integration_adaptors_logger.IntegrationAdaptorsLogger.audit')
    @async_test
    async def test_unhandled_response_from_spine(self, audit_log_mock):
        self.setup_mock_work_description()
        self._setup_routing_mock()

        self.mock_ebxml_request_envelope.return_value.serialize.return_value = (MESSAGE_ID, {}, SERIALIZED_MESSAGE)

        response = mock.MagicMock()
        response.code = 400
        response.headers = {'Content-Type': 'text/xml'}
        response.body = '<a></a>'
        self.mock_transmission_adaptor.make_request.return_value = test_utilities.awaitable(response)

        with mock.patch('utilities.config.get_config', return_value='localhost/reliablemessaging/queryrequest'):
            status, message, _ = await self.workflow.handle_outbound_message(None, MESSAGE_ID, CORRELATION_ID,
                                                                             INTERACTION_DETAILS,
                                                                             PAYLOAD, None)

        self.assertEqual(500, status)
        self.assertEqual("Didn't get expected response from Spine", message)
        self.mock_work_description.publish.assert_called_once()
        self.assertEqual(
            [mock.call(MessageStatus.OUTBOUND_MESSAGE_NACKD)],
            self.mock_work_description.set_outbound_status.call_args_list)
        audit_log_mock.assert_called_once_with('Outbound {WorkflowName} workflow invoked.',
                                               fparams={'WorkflowName': 'forward-reliable'})

    @mock.patch('utilities.integration_adaptors_logger.IntegrationAdaptorsLogger.audit')
    @async_test
    async def test_well_formed_ebxml_error_response_from_spine(self, audit_log_mock):
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

        with mock.patch('utilities.config.get_config', return_value='localhost/reliablemessaging/queryrequest'):
            status, message, _ = await self.workflow.handle_outbound_message(None, MESSAGE_ID, CORRELATION_ID,
                                                                             INTERACTION_DETAILS, PAYLOAD, None)

        self.mock_work_description.publish.assert_called_once()
        self.assertEqual(
            [mock.call(MessageStatus.OUTBOUND_MESSAGE_NACKD)],
            self.mock_work_description.set_outbound_status.call_args_list)
        audit_log_mock.assert_called_once_with('Outbound {WorkflowName} workflow invoked.',
                                               fparams={'WorkflowName': 'forward-reliable'})

    ############################
    # Reliability tests
    ############################

    @async_test
    async def test_retry_interval_contract_property_is_invalid(self):
        self.setup_mock_work_description()
        self._setup_routing_mock()

        self.mock_routing_reliability.get_reliability.return_value = test_utilities.awaitable({
            workflow.common_asynchronous.MHS_RETRY_INTERVAL: MHS_RETRY_INTERVAL_INVALID_VAL,
            workflow.common_asynchronous.MHS_RETRIES: MHS_RETRY_VAL})

        self.mock_ebxml_request_envelope.return_value.serialize.return_value = (MESSAGE_ID, {}, SERIALIZED_MESSAGE)

        message = file_utilities.get_file_string(Path(self.test_message_dir) / 'soapfault_response_single_error.xml')

        response = httpclient.HTTPResponse
        response.code = 500
        response.body = message
        response.headers = {'Content-Type': 'text/xml'}

        self.mock_transmission_adaptor.make_request.return_value = test_utilities.awaitable(response)

        with mock.patch('utilities.config.get_config', return_value='localhost/reliablemessaging/queryrequest'):
            status, message, _ = await self.workflow.handle_outbound_message(None, MESSAGE_ID, CORRELATION_ID,
                                                                             INTERACTION_DETAILS,
                                                                             PAYLOAD, None)

        self.assertEqual(500, status)
        self.assertTrue('Error when converting retry interval' in message)
        self.assertEqual(
            [mock.call(MessageStatus.OUTBOUND_MESSAGE_PREPARATION_FAILED)],
            self.mock_work_description.set_outbound_status.call_args_list)

    @mock.patch('asyncio.sleep')
    @async_test
    async def test_soap_error_request_is_retriable(self, mock_sleep):
        self.setup_mock_work_description()
        self._setup_routing_mock()
        mock_sleep.return_value = test_utilities.awaitable(None)

        self.mock_ebxml_request_envelope.return_value.serialize.return_value = (MESSAGE_ID, {}, SERIALIZED_MESSAGE)

        sub_tests = [
            ("a retriable soap 200 error code", 'soapfault_response_single_error.xml'),
            ("a retriable soap 206 error code", 'soapfault_response_single_error_206.xml'),
            ("a retriable soap 208 error code", 'soapfault_response_single_error_208.xml')
        ]
        for description, soap_fault_file_path in sub_tests:
            with self.subTest(description):
                try:
                    response = mock.MagicMock()
                    response.code = 500
                    response.headers = {'Content-Type': 'text/xml'}
                    response.body = file_utilities.get_file_string(Path(self.test_message_dir) / soap_fault_file_path)
                    self.mock_transmission_adaptor.make_request.return_value = test_utilities.awaitable(response)

                    with mock.patch('utilities.config.get_config',
                                    return_value='localhost/reliablemessaging/queryrequest'):
                        await self.workflow.handle_outbound_message(None, MESSAGE_ID, CORRELATION_ID,
                                                                    INTERACTION_DETAILS, PAYLOAD, None)

                    self.assertEqual(self.mock_transmission_adaptor.make_request.call_count, 4)
                    self.assertEqual(mock_sleep.call_count, 3)
                    mock_sleep.assert_called_with(MHS_RETRY_INTERVAL_VAL_IN_SECONDS)
                finally:
                    self.mock_transmission_adaptor.make_request.reset_mock()
                    mock_sleep.reset_mock()

    @mock.patch('asyncio.sleep')
    @async_test
    async def test_soap_error_request_retry_logic_makes_two_requests_if_retry_is_set_to_one(self, mock_sleep):
        self.workflow = forward_reliable.AsynchronousForwardReliableWorkflow(
            party_key=FROM_PARTY_KEY,
            persistence_store=self.mock_persistence_store,
            transmission=self.mock_transmission_adaptor,
            queue_adaptor=self.mock_queue_adaptor,
            max_request_size=MAX_REQUEST_SIZE,
            routing=self.mock_routing_reliability
        )

        self.setup_mock_work_description()
        self._setup_routing_mock()
        mock_sleep.return_value = test_utilities.awaitable(None)

        self.mock_ebxml_request_envelope.return_value.serialize.return_value = (MESSAGE_ID, {}, SERIALIZED_MESSAGE)

        error_response = mock.MagicMock()
        error_response.code = 500
        error_response.headers = {'Content-Type': 'text/xml'}
        error_response.body = file_utilities.get_file_string(
            Path(self.test_message_dir) / 'soapfault_response_single_error.xml')

        success_response = mock.MagicMock()
        success_response.code = 202

        self.mock_transmission_adaptor.make_request.side_effect = [test_utilities.awaitable(error_response),
                                                                   test_utilities.awaitable(success_response)]
        with mock.patch('utilities.config.get_config', return_value='localhost/reliablemessaging/queryrequest'):
            await self.workflow.handle_outbound_message(None, MESSAGE_ID, CORRELATION_ID,
                                                        INTERACTION_DETAILS, PAYLOAD, None)

        self.assertEqual(self.mock_transmission_adaptor.make_request.call_count, 2)
        mock_sleep.assert_called_once_with(MHS_RETRY_INTERVAL_VAL_IN_SECONDS)

    @async_test
    async def test_soap_error_request_is_non_retriable(self):
        self.setup_mock_work_description()
        self._setup_routing_mock()

        self.mock_ebxml_request_envelope.return_value.serialize.return_value = (MESSAGE_ID, {}, SERIALIZED_MESSAGE)

        response = mock.MagicMock()
        response.code = 500
        response.headers = {'Content-Type': 'text/xml'}
        # a non retriable soap 300 error code
        response.body = file_utilities.get_file_string(
            Path(self.test_message_dir) / 'soapfault_response_single_error_300.xml')
        self.mock_transmission_adaptor.make_request.return_value = test_utilities.awaitable(response)

        with mock.patch('utilities.config.get_config', return_value='localhost/reliablemessaging/queryrequest'):
            status, message, _ = await self.workflow.handle_outbound_message(None, MESSAGE_ID, CORRELATION_ID,
                                                                             INTERACTION_DETAILS, PAYLOAD, None)

        self.mock_transmission_adaptor.make_request.assert_called_once()

    ############################
    # Inbound tests
    ############################

    @mock.patch('utilities.integration_adaptors_logger.IntegrationAdaptorsLogger.audit')
    @async_test
    async def test_successful_handle_inbound_message(self, audit_log_mock):
        self.setup_mock_work_description()
        self.mock_queue_adaptor.send_async.return_value = test_utilities.awaitable(None)

        await self.workflow.handle_inbound_message(MESSAGE_ID, CORRELATION_ID, self.mock_work_description, INBOUND_MESSAGE_DATA)

        self.mock_queue_adaptor.send_async.assert_called_once_with(
            {'ebXML': EBXML, 'payload': PAYLOAD, 'attachments': ATTACHMENTS},
            properties={'message-id': MESSAGE_ID, 'correlation-id': CORRELATION_ID})
        self.assertEqual([mock.call(MessageStatus.INBOUND_RESPONSE_SUCCESSFULLY_PROCESSED)],
                         self.mock_work_description.set_inbound_status.call_args_list)
        audit_log_mock.assert_called_with('{WorkflowName} inbound workflow completed. Message placed on queue,'
                                          ' returning {Acknowledgement} to spine',
                                          fparams={
                                              'Acknowledgement': 'INBOUND_RESPONSE_SUCCESSFULLY_PROCESSED',
                                              'WorkflowName': 'forward-reliable'
                                          })

    @mock.patch('utilities.integration_adaptors_logger.IntegrationAdaptorsLogger.audit')
    @mock.patch('asyncio.sleep')
    @async_test
    async def test_handle_inbound_message_error_putting_message_onto_queue_despite_retries(self, mock_sleep,
                                                                                           audit_log_mock):
        self.setup_mock_work_description()
        future = asyncio.Future()
        future.set_exception(proton_queue_adaptor.MessageSendingError())
        self.mock_queue_adaptor.send_async.return_value = future
        mock_sleep.return_value = test_utilities.awaitable(None)

        with self.assertRaises(proton_queue_adaptor.MessageSendingError):
            await self.workflow.handle_inbound_message(MESSAGE_ID, CORRELATION_ID, self.mock_work_description, INBOUND_MESSAGE_DATA)

        self.assertEqual([mock.call(MessageStatus.INBOUND_RESPONSE_FAILED)],
                         self.mock_work_description.set_inbound_status.call_args_list)
        # Should be called when invoked
        audit_log_mock.assert_called_once_with('{WorkflowName} inbound workflow invoked. Message '
                                               'received from spine', fparams={'WorkflowName': 'forward-reliable'})

    ############################
    # Inbound unsolicited tests
    ############################

    @mock.patch('utilities.integration_adaptors_logger.IntegrationAdaptorsLogger.audit')
    @async_test
    async def test_successful_handle_unsolicited_inbound_message(self, audit_log_mock):
        self.setup_mock_work_description()
        self.mock_queue_adaptor.send_async.return_value = test_utilities.awaitable(None)

        await self.workflow.handle_unsolicited_inbound_message(MESSAGE_ID, CORRELATION_ID, INBOUND_MESSAGE_DATA)

        self.mock_queue_adaptor.send_async.assert_called_once_with(
            {'ebXML': EBXML, 'payload': PAYLOAD, 'attachments': ATTACHMENTS},
            properties={'message-id': MESSAGE_ID, 'correlation-id': CORRELATION_ID})
        self.mock_create_new_work_description.assert_called_once_with(self.mock_persistence_store, MESSAGE_ID,
                                                                      workflow.FORWARD_RELIABLE,
                                                                      MessageStatus.
                                                                      UNSOLICITED_INBOUND_RESPONSE_RECEIVED)
        self.mock_work_description.publish.assert_called_once()
        audit_log_mock.assert_called_with('{WorkflowName} workflow invoked for inbound unsolicited request. '
                                          'Attempted to place message onto inbound queue with '
                                          '{Acknowledgement}.',
                                          fparams={
                                              'Acknowledgement': 'UNSOLICITED_INBOUND_RESPONSE_SUCCESSFULLY_PROCESSED',
                                              'WorkflowName': 'forward-reliable'
                                          })
        self.assertEqual([mock.call(MessageStatus.UNSOLICITED_INBOUND_RESPONSE_SUCCESSFULLY_PROCESSED)],
                         self.mock_work_description.set_inbound_status.call_args_list)

    @mock.patch('utilities.integration_adaptors_logger.IntegrationAdaptorsLogger.audit')
    @mock.patch('asyncio.sleep')
    @async_test
    async def test_handle_unsolicited_inbound_message_error_putting_message_onto_queue_despite_retries(self, mock_sleep,
                                                                                                       audit_log_mock):
        self.setup_mock_work_description()
        future = asyncio.Future()
        future.set_exception(proton_queue_adaptor.MessageSendingError())
        self.mock_queue_adaptor.send_async.return_value = future
        mock_sleep.return_value = test_utilities.awaitable(None)

        with self.assertRaises(proton_queue_adaptor.MessageSendingError):
            await self.workflow.handle_unsolicited_inbound_message(MESSAGE_ID, CORRELATION_ID, INBOUND_MESSAGE_DATA)

        audit_log_mock.assert_called_with('Unsolicited inbound {WorkflowName} workflow invoked.',
                                          fparams={'WorkflowName': 'forward-reliable'})
        self.assertEqual([mock.call(MessageStatus.UNSOLICITED_INBOUND_RESPONSE_FAILED)],
                         self.mock_work_description.set_inbound_status.call_args_list)

    ############################
    # Helper methods
    ############################

    def setup_mock_work_description(self):
        self.mock_work_description = self.mock_create_new_work_description.return_value
        self.mock_work_description.publish.return_value = test_utilities.awaitable(None)
        self.mock_work_description.set_outbound_status.return_value = test_utilities.awaitable(None)
        self.mock_work_description.set_inbound_status.return_value = test_utilities.awaitable(None)
        self.mock_work_description.update.return_value = test_utilities.awaitable(None)

    def _setup_routing_mock(self):
        self.mock_routing_reliability.get_end_point.return_value = test_utilities.awaitable({
            MHS_END_POINT_KEY: [URL],
            MHS_TO_PARTY_KEY_KEY: TO_PARTY_KEY,
            MHS_CPA_ID_KEY: CPA_ID,
            MHS_ASID: [ASID]
        })
        self.mock_routing_reliability.get_reliability.return_value = test_utilities.awaitable({
            workflow.common_asynchronous.MHS_RETRY_INTERVAL: MHS_RETRY_INTERVAL_VAL,
            workflow.common_asynchronous.MHS_RETRIES: MHS_RETRY_VAL})
