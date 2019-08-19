import asyncio
import unittest
from unittest import mock

import requests
from utilities import test_utilities
from utilities.test_utilities import async_test

import mhs_common.workflow.asynchronous_express as async_express
from mhs_common import workflow
from mhs_common.messages import ebxml_request_envelope, ebxml_envelope
from mhs_common.state import work_description
from mhs_common.state.work_description import MessageStatus

PARTY_KEY = 'party-key'
MESSAGE_ID = 'message-id'
CORRELATION_ID = 'correlation-id'
INTERACTION_DETAILS = {'workflow': 'async-express'}
PAYLOAD = 'payload'
SERIALIZED_MESSAGE = 'serialized-message'


class TestAsynchronousExpressWorkflow(unittest.TestCase):
    def setUp(self):
        self.mock_persistence_store = mock.MagicMock()
        self.mock_transmission_adaptor = mock.MagicMock()

        patcher = mock.patch.object(work_description, 'create_new_work_description')
        self.mock_create_new_work_description = patcher.start()
        self.addCleanup(patcher.stop)

        patcher = mock.patch.object(ebxml_request_envelope, 'EbxmlRequestEnvelope')
        self.mock_ebxml_request_envelope = patcher.start()
        self.addCleanup(patcher.stop)

        self.workflow = async_express.AsynchronousExpressWorkflow(PARTY_KEY, self.mock_persistence_store,
                                                                  self.mock_transmission_adaptor)

    @mock.patch.object(async_express, 'logger')
    @async_test
    async def test_handle_outbound_message(self, log_mock):
        response = mock.MagicMock()
        response.status_code = 202

        self.setup_mock_work_description()

        self.mock_ebxml_request_envelope.return_value.serialize.return_value = (MESSAGE_ID, {}, SERIALIZED_MESSAGE)
        self.mock_transmission_adaptor.make_request.return_value = test_utilities.awaitable(response)

        expected_interaction_details = {ebxml_envelope.MESSAGE_ID: MESSAGE_ID, ebxml_request_envelope.MESSAGE: PAYLOAD,
                                        ebxml_envelope.FROM_PARTY_ID: PARTY_KEY,
                                        ebxml_envelope.CONVERSATION_ID: CORRELATION_ID}
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
        self.mock_ebxml_request_envelope.assert_called_once_with(expected_interaction_details)
        self.mock_transmission_adaptor.make_request.assert_called_once_with(expected_interaction_details,
                                                                            SERIALIZED_MESSAGE)
        self.assert_audit_log_recorded_with_message_status(log_mock, MessageStatus.OUTBOUND_MESSAGE_ACKD)

    @async_test
    async def test_handle_outbound_message_serialisation_fails(self):
        self.setup_mock_work_description()

        self.mock_ebxml_request_envelope.return_value.serialize.side_effect = Exception()

        status, message = await self.workflow.handle_outbound_message(MESSAGE_ID, CORRELATION_ID, INTERACTION_DETAILS,
                                                                      PAYLOAD)

        self.assertEqual(500, status)
        self.assertEqual('Error serialising outbound message', message)
        self.mock_work_description.publish.assert_called_once()
        self.assertEqual([mock.call(MessageStatus.OUTBOUND_MESSAGE_PREPARATION_FAILED)],
                         self.mock_work_description.set_status.call_args_list)
        self.mock_transmission_adaptor.make_request.assert_not_called()

    @mock.patch.object(async_express, 'logger')
    @async_test
    async def test_handle_outbound_message_http_error_when_calling_outbound_transmission(self, log_mock):
        self.setup_mock_work_description()

        self.mock_ebxml_request_envelope.return_value.serialize.return_value = (MESSAGE_ID, {}, SERIALIZED_MESSAGE)

        response = mock.MagicMock()
        response.status_code = 409
        future = asyncio.Future()
        future.set_exception(requests.exceptions.HTTPError(response=response))
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

        self.mock_ebxml_request_envelope.return_value.serialize.return_value = (MESSAGE_ID, {}, SERIALIZED_MESSAGE)

        response = mock.MagicMock()
        response.status_code = 200
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

    def setup_mock_work_description(self):
        self.mock_work_description = self.mock_create_new_work_description.return_value
        self.mock_work_description.publish.return_value = test_utilities.awaitable(None)
        self.mock_work_description.set_status.return_value = test_utilities.awaitable(None)

    def assert_audit_log_recorded_with_message_status(self, log_mock, message_status):
        log_mock.audit.assert_called_once()
        audit_log_dict = log_mock.audit.call_args[0][2]
        self.assertEqual(message_status, audit_log_dict['Acknowledgment'])
