import asyncio
import unittest
from unittest import mock

from tornado import httpclient

from mhs_common.messages import soap_envelope
from mhs_common.workflow import synchronous as sync
from mhs_common import workflow
from mhs_common.state import work_description
from utilities import test_utilities
from utilities.test_utilities import async_test

PARTY_KEY = "313"
LOOKUP_RESPONSE = {
    'url': 'url123',
    'to_asid': 'asid'
}
MAX_REQUEST_SIZE = 5000000


class TestSynchronousWorkflow(unittest.TestCase):

    def setUp(self) -> None:
        self.wd_store = mock.MagicMock()
        self.transmission = mock.MagicMock()
        self.routing_mock = mock.MagicMock()
        self.wf = sync.SynchronousWorkflow(
            PARTY_KEY,
            work_description_store=self.wd_store,
            transmission=self.transmission,
            max_request_size=MAX_REQUEST_SIZE,
            persistence_store_max_retries=3,
            routing=self.routing_mock
        )

    @mock.patch('mhs_common.state.work_description.create_new_work_description')
    @async_test
    async def test_should_set_store_outbound_status_to_received_when_handling_outbound_message(self, wd_mock):
        wdo_mock = mock.MagicMock()
        wd_mock.return_value = wdo_mock

        try:
            await self.wf.handle_outbound_message(from_asid="202020", message_id="123",
                                                  correlation_id="qwe",
                                                  interaction_details={},
                                                  payload="nice message", work_description_object=None)
        except Exception:
            # Don't care for exceptions, just want to check the store is set correctly first
            pass

        wd_mock.assert_called_with(self.wd_store, "123", workflow.SYNC,
                                   outbound_status=work_description.MessageStatus.OUTBOUND_MESSAGE_RECEIVED)
        wdo_mock.publish.assert_called_once()

    @mock.patch.object(sync, 'logger')
    @mock.patch('mhs_common.state.work_description.create_new_work_description')
    @async_test
    async def test_asid_lookup_failure_set_store(self, wd_mock, log_mock):
        wdo = mock.MagicMock()
        wdo.publish.return_value = test_utilities.awaitable(None)
        wd_mock.return_value = wdo
        self.wf._lookup_to_asid_details = mock.MagicMock()
        self.wf._lookup_to_asid_details.side_effect = Exception()
        wdo.set_outbound_status.return_value = test_utilities.awaitable(None)

        error, text, work_description_response = await self.wf.handle_outbound_message(from_asid="202020",
                                                                                       message_id="123",
                                                                                       correlation_id="qwe",
                                                                                       interaction_details={},
                                                                                       payload="nice message",
                                                                                       work_description_object=None)

        wdo.set_outbound_status.assert_called_with(work_description.MessageStatus.OUTBOUND_MESSAGE_PREPARATION_FAILED)
        self.assertEqual(error, 500)
        self.assertEqual(text, 'Error obtaining outbound URL')

    @mock.patch.object(sync, 'logger')
    @mock.patch('mhs_common.state.work_description.create_new_work_description')
    @async_test
    async def test_prepare_message_failure(self, wd_mock, log_mock):
        wdo = mock.MagicMock()
        wdo.publish.return_value = test_utilities.awaitable(None)
        wd_mock.return_value = wdo
        self.wf._lookup_endpoint_details = mock.MagicMock()
        self.wf._lookup_endpoint_details.return_value = test_utilities.awaitable(LOOKUP_RESPONSE)
        self.wf._prepare_outbound_message = mock.MagicMock()
        self.wf._prepare_outbound_message.side_effect = Exception()
        wdo.set_outbound_status.return_value = test_utilities.awaitable(None)

        error, text, work_description_response = await self.wf.handle_outbound_message(from_asid="202020",
                                                                                       message_id="123",
                                                                                       correlation_id="qwe",
                                                                                       interaction_details={},
                                                                                       payload="nice message",
                                                                                       work_description_object=None)

        wdo.set_outbound_status.assert_called_with(work_description.MessageStatus.OUTBOUND_MESSAGE_PREPARATION_FAILED)
        self.assertEqual(error, 500)
        self.assertEqual(text, 'Failed message preparation')
        log_mock.exception.assert_called_with('Failed to prepare outbound message')

    @mock.patch('mhs_common.messages.soap_envelope.SoapEnvelope')
    @mock.patch('mhs_common.state.work_description.create_new_work_description')
    @async_test
    async def test_prepare_message_success_but_message_too_large(self, wd_mock, mock_soap_envelope):
        wdo = mock.MagicMock()
        wdo.publish.return_value = test_utilities.awaitable(None)
        wd_mock.return_value = wdo
        self.wf._lookup_endpoint_details = mock.MagicMock()
        self.wf._lookup_endpoint_details.return_value = test_utilities.awaitable(LOOKUP_RESPONSE)
        wdo.set_outbound_status.return_value = test_utilities.awaitable(None)
        mock_soap_envelope.return_value.serialize.return_value = ('message-id', {}, 'e' * (MAX_REQUEST_SIZE + 1))

        test_interaction_details = {'service': 'test-service', 'action': 'test-action'}
        error, text, work_description_response = await self.wf.handle_outbound_message(
            from_asid="202020",
            message_id="123",
            correlation_id="qwe",
            interaction_details=test_interaction_details,
            payload="nice message",
            work_description_object=None)

        wdo.set_outbound_status.assert_called_with(work_description.MessageStatus.OUTBOUND_MESSAGE_PREPARATION_FAILED)
        self.assertEqual(error, 400)
        self.assertIn('Request to send to Spine is too large', text)

    @mock.patch.object(sync, 'logger')
    @mock.patch('mhs_common.state.work_description.create_new_work_description')
    @async_test
    async def test_send_message_failure(self, wd_mock, log_mock):
        wdo = mock.MagicMock()
        wdo.publish.return_value = test_utilities.awaitable(None)
        wd_mock.return_value = wdo
        self.wf._lookup_endpoint_details = mock.MagicMock()
        self.wf._lookup_endpoint_details.return_value = test_utilities.awaitable(LOOKUP_RESPONSE)
        self.wf._prepare_outbound_message = mock.MagicMock()
        self.wf._prepare_outbound_message.return_value = test_utilities.awaitable(("123", {"qwe": "qwe"}, "message"))
        self.wf.transmission.make_request.side_effect = Exception("failed")
        wdo.set_outbound_status.return_value = test_utilities.awaitable(None)

        error, text, work_description_response = await self.wf.handle_outbound_message(
            from_asid="202020",
            message_id="123",
            correlation_id="qwe",
            interaction_details={'action': ''},
            payload="nice message",
            work_description_object=None)

        wdo.set_outbound_status.assert_called_with(work_description.MessageStatus.OUTBOUND_MESSAGE_TRANSMISSION_FAILED)
        self.assertEqual(error, 500)
        self.assertEqual(text, 'Error making outbound request')

        log_call = log_mock.exception.call_args
        self.assertEqual(log_call[0][0], 'Error encountered whilst making outbound request.')

    @mock.patch.object(sync, 'logger')
    @mock.patch('mhs_common.state.work_description.create_new_work_description')
    @async_test
    async def test_send_message_http_error(self, wd_mock, log_mock):
        wdo = mock.MagicMock()
        wdo.publish.return_value = test_utilities.awaitable(None)
        wd_mock.return_value = wdo
        self.wf._lookup_endpoint_details = mock.MagicMock()
        self.wf._lookup_endpoint_details.return_value = test_utilities.awaitable(LOOKUP_RESPONSE)
        self.wf._prepare_outbound_message = mock.MagicMock()
        self.wf._prepare_outbound_message.return_value = test_utilities.awaitable(("123", {"qwe": "qwe"}, "message"))
        wdo.set_outbound_status.return_value = test_utilities.awaitable(None)
        future = asyncio.Future()
        future.set_exception(httpclient.HTTPClientError(code=409))
        self.transmission.make_request.return_value = future

        error, text, work_description_response = await self.wf.handle_outbound_message(
            from_asid="202020",
            message_id="123",
            correlation_id="qwe",
            interaction_details={'action': ''},
            payload="nice message",
            work_description_object=None)

        wdo.set_outbound_status.assert_called_with(work_description.MessageStatus.OUTBOUND_SYNC_MESSAGE_RESPONSE_RECEIVED)
        self.assertEqual(error, 500)
        self.assertEqual(text, 'Error(s) received from Spine: HTTP 409: Conflict')

    @mock.patch('mhs_common.state.work_description.create_new_work_description')
    @async_test
    async def test_send_message_http_status_code_err(self, wd_mock):
        self._setup_success_workflow()
        wdo = mock.MagicMock()
        wdo.publish.return_value = test_utilities.awaitable(None)
        wd_mock.return_value = wdo
        wdo.set_outbound_status.return_value = test_utilities.awaitable(None)

        future = asyncio.Future()
        future.set_exception(httpclient.HTTPClientError(code=451))
        self.transmission.make_request.return_value = future

        error, text, work_description_response = await self.wf.handle_outbound_message(
            from_asid="202020",
            message_id="123",
            correlation_id="qwe",
            interaction_details={'action': ''},
            payload="nice message",
            work_description_object=None)

        wdo.set_outbound_status.assert_called_with(work_description.MessageStatus.OUTBOUND_SYNC_MESSAGE_RESPONSE_RECEIVED)
        self.assertEqual(error, 500)
        self.assertEqual(text[:40], 'Error(s) received from Spine: HTTP 451: ')

    @mock.patch('mhs_common.state.work_description.create_new_work_description')
    @async_test
    async def test_send_message_success_message(self, wd_mock):
        self._setup_success_workflow()
        wdo = mock.MagicMock()
        wdo.publish.return_value = test_utilities.awaitable(None)
        wd_mock.return_value = wdo
        wdo.set_outbound_status.return_value = test_utilities.awaitable(None)

        error, text, work_description_response = await self.wf.handle_outbound_message(
            from_asid="202020",
            message_id="123",
            correlation_id="qwe",
            interaction_details={'action': 'test-interaction'},
            payload="nice message",
            work_description_object=None)

        wdo.set_outbound_status.assert_called_with(work_description.MessageStatus.OUTBOUND_SYNC_MESSAGE_RESPONSE_RECEIVED)
        self.assertEqual(error, 200)
        self.assertEqual(text, 'response body')

    @mock.patch('mhs_common.workflow.synchronous.logger')
    @mock.patch('mhs_common.state.work_description.create_new_work_description')
    @async_test
    async def test_success_audit_log_should_be_called_when_successful_response_is_returned_from_spine(self, wd_mock,
                                                                                                      log_mock):
        self._setup_success_workflow()
        wdo = mock.MagicMock()
        wdo.publish.return_value = test_utilities.awaitable(None)
        wd_mock.return_value = wdo
        wdo.set_outbound_status.return_value = test_utilities.awaitable(None)

        await self.wf.handle_outbound_message(
            from_asid="202020",
            message_id="123",
            correlation_id="qwe",
            interaction_details={'action': 'test-interaction'},
            payload="nice message",
            work_description_object=None)

        log_mock.audit.assert_called_with(
            'Outbound Synchronous workflow completed. Message sent to Spine and {Acknowledgment} received.',
            fparams={'Acknowledgment': 'OUTBOUND_SYNC_MESSAGE_RESPONSE_RECEIVED'})

    @mock.patch('mhs_common.workflow.synchronous.logger')
    @mock.patch('mhs_common.state.work_description.create_new_work_description')
    @async_test
    async def test_initial_audit_log_should_be_called_handling_is_invoked(self, wd_mock, log_mock):
        self._setup_success_workflow()
        wdo = mock.MagicMock()
        wdo.publish.return_value = test_utilities.awaitable(None)
        wd_mock.return_value = wdo
        wdo.set_outbound_status.return_value = test_utilities.awaitable(None)

        future = asyncio.Future()
        future.set_exception(httpclient.HTTPClientError(code=451))
        self.transmission.make_request.return_value = future

        await self.wf.handle_outbound_message(
            from_asid="202020",
            message_id="123",
            correlation_id="qwe",
            interaction_details={'action': 'test-interaction'},
            payload="nice message",
            work_description_object=None)

        # audit log should be called at start
        log_mock.audit('Outbound Synchronous workflow invoked.')

    @mock.patch('mhs_common.state.work_description.create_new_work_description')
    @async_test
    async def test_handle_outbound_errors_when_no_asid_provided(self, wd_mock):
        wdo = mock.MagicMock()
        wdo.publish.return_value = test_utilities.awaitable(None)
        wd_mock.return_value = wdo
        wdo.set_outbound_status.return_value = test_utilities.awaitable(None)

        error, text, work_description_response = await self.wf.handle_outbound_message(from_asid=None,
                                                                                       message_id="123",
                                                                                       correlation_id="qwe",
                                                                                       interaction_details={},
                                                                                       payload="nice message",
                                                                                       work_description_object=None)

        self.assertEqual(error, 400)
        self.assertEqual(text, '`from_asid` header field required for sync messages')

    @async_test
    async def test_no_inbound(self):
        with self.assertRaises(NotImplementedError):
            await self.wf.handle_inbound_message("1", "2", mock.MagicMock(), "payload")

    @async_test
    async def test_prepare_message(self):
        id, headers, message = await self.wf._prepare_outbound_message("message_id", "to_asid", "from_asid", "mesasge",
                                                                       {'service': 'service', 'action': 'action'})
        self.assertEqual(id, "message_id")
        self.assertEqual(headers, {'Content-Type': 'text/xml',
                                   'SOAPAction': 'service/action',
                                   'charset': 'UTF-8',
                                   'type': 'text/xml'})

    @mock.patch('mhs_common.messages.soap_envelope.SoapEnvelope')
    @async_test
    async def test_prepare_message_correct_constructor_call(self, envelope_patch):
        envelope = mock.MagicMock()
        envelope_patch.return_value = envelope
        await self.wf._prepare_outbound_message("message_id", "to_asid", "from_asid", "Message123",
                                                {'service': 'service', 'action': 'action'})
        message_details = {
            soap_envelope.MESSAGE_ID: "message_id",
            soap_envelope.TO_ASID: 'to_asid',
            soap_envelope.FROM_ASID: 'from_asid',
            soap_envelope.SERVICE: 'service',
            soap_envelope.ACTION: 'service/action',
            soap_envelope.MESSAGE: 'Message123'
        }

        envelope_patch.assert_called_with(message_details)
        envelope.serialize.assert_called_once()

    @mock.patch('mhs_common.messages.soap_envelope.SoapEnvelope.serialize')
    @async_test
    async def test_prepare_message_raises_exception(self, serialize_mock):
        serialize_mock.side_effect = Exception()
        with self.assertRaises(Exception):
            await self.wf._prepare_outbound_message("message_id", "to_asid", "from_asid", "mesasge",
                                                    {'service': 'service', 'action': 'action'})

    @async_test
    async def test_success_response(self):
        wdo = mock.MagicMock()
        wdo.publish.return_value = test_utilities.awaitable(None)
        wdo.set_outbound_status.return_value = test_utilities.awaitable(None)

        await self.wf.set_successful_message_response(wdo)
        wdo.set_outbound_status.assert_called_once_with(work_description.MessageStatus.SYNC_RESPONSE_SUCCESSFUL)

    @async_test
    async def test_failure_response(self):
        wdo = mock.MagicMock()
        wdo.publish.return_value = test_utilities.awaitable(None)
        wdo.set_outbound_status.return_value = test_utilities.awaitable(None)

        await self.wf.set_failure_message_response(wdo)
        wdo.set_outbound_status.assert_called_once_with(work_description.MessageStatus.SYNC_RESPONSE_FAILED)

    def _setup_success_workflow(self):
        self.wf._lookup_endpoint_details = mock.MagicMock()
        self.wf._lookup_endpoint_details.return_value = test_utilities.awaitable(LOOKUP_RESPONSE)
        self.wf._prepare_outbound_message = mock.MagicMock()
        self.wf._prepare_outbound_message.return_value = test_utilities.awaitable(("123", {"qwe": "qwe"}, "message"))
        response = mock.MagicMock()
        response.code = 200
        response.body = b'response body'
        self.transmission.make_request.return_value = test_utilities.awaitable(response)
