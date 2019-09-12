import asyncio
import unittest
from unittest import mock

from tornado import httpclient

from mhs_common.workflow import synchronous as sync
from mhs_common import workflow
from mhs_common.state import work_description
from utilities import test_utilities
from utilities.test_utilities import async_test

PARTY_KEY = "313"


class TestSynchronousWorkflow(unittest.TestCase):

    def setUp(self) -> None:
        self.wd_store = mock.MagicMock()
        self.transmission = mock.MagicMock()
        self.routing_mock = mock.MagicMock()
        self.wf = sync.SynchronousWorkflow(
            PARTY_KEY,
            work_description_store=self.wd_store,
            transmission=self.transmission,
            persistence_store_max_retries=3,
            routing=self.routing_mock
        )

    @mock.patch('mhs_common.state.work_description.create_new_work_description')
    @async_test
    async def test_store_status_set_to_received(self, wd_mock):
        try:
            await self.wf.handle_outbound_message(message_id="123",
                                                  correlation_id="qwe",
                                                  interaction_details={},
                                                  payload="nice message", work_description_object=None)
        except Exception:
            # Don't care for exceptions, just want to check the store is set correctly first
            pass

        wd_mock.assert_called_with(self.wd_store, "123", workflow.SYNC,
                                   work_description.MessageStatus.OUTBOUND_MESSAGE_RECEIVED)

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

        error, text = await self.wf.handle_outbound_message(message_id="123",
                                                            correlation_id="qwe",
                                                            interaction_details={},
                                                            payload="nice message", work_description_object=None)

        wdo.set_outbound_status.assert_called_with(work_description.MessageStatus.OUTBOUND_MESSAGE_PREPARATION_FAILED)
        self.assertEqual(error, 500)
        self.assertEqual(text, 'Error obtaining outbound URL')
        log_mock.error.assert_called_with('009', 'Failed to retrieve details from spine route lookup')

    @mock.patch.object(sync, 'logger')
    @mock.patch('mhs_common.state.work_description.create_new_work_description')
    @async_test
    async def test_prepare_message_failure(self, wd_mock, log_mock):
        wdo = mock.MagicMock()
        wdo.publish.return_value = test_utilities.awaitable(None)
        wd_mock.return_value = wdo
        self.wf._lookup_to_asid_details = mock.MagicMock()
        self.wf._lookup_to_asid_details.return_value = test_utilities.awaitable(("yes", "313123"))
        self.wf._prepare_outbound_message = mock.MagicMock()
        self.wf._prepare_outbound_message.side_effect = Exception()
        wdo.set_outbound_status.return_value = test_utilities.awaitable(None)

        error, text = await self.wf.handle_outbound_message(message_id="123",
                                                            correlation_id="qwe",
                                                            interaction_details={},
                                                            payload="nice message", work_description_object=None)

        wdo.set_outbound_status.assert_called_with(work_description.MessageStatus.OUTBOUND_MESSAGE_PREPARATION_FAILED)
        self.assertEqual(error, 500)
        self.assertEqual(text, 'Failed message preparation')
        log_mock.error.assert_called_with('002', 'Failed to prepare outbound message')

    @mock.patch('mhs_common.state.work_description.create_new_work_description')
    @async_test
    async def test_send_message_failure(self, wd_mock):
        wdo = mock.MagicMock()
        wdo.publish.return_value = test_utilities.awaitable(None)
        wd_mock.return_value = wdo
        self.wf._lookup_to_asid_details = mock.MagicMock()
        self.wf._lookup_to_asid_details.return_value = test_utilities.awaitable(("yes", "313123"))
        self.wf._prepare_outbound_message = mock.MagicMock()
        self.wf._prepare_outbound_message.return_value = test_utilities.awaitable(("123", {"qwe": "qwe"}, "message"))
        wdo.set_outbound_status.return_value = test_utilities.awaitable(None)

        error, text = await self.wf.handle_outbound_message(message_id="123",
                                                            correlation_id="qwe",
                                                            interaction_details={},
                                                            payload="nice message", work_description_object=None)

        wdo.set_outbound_status.assert_called_with(work_description.MessageStatus.OUTBOUND_MESSAGE_TRANSMISSION_FAILED)
        self.assertEqual(error, 500)
        self.assertEqual(text, 'Error making outbound request')

    @mock.patch('mhs_common.state.work_description.create_new_work_description')
    @async_test
    async def test_send_message_http_error(self, wd_mock):
        wdo = mock.MagicMock()
        wdo.publish.return_value = test_utilities.awaitable(None)
        wd_mock.return_value = wdo
        self.wf._lookup_to_asid_details = mock.MagicMock()
        self.wf._lookup_to_asid_details.return_value = test_utilities.awaitable(("yes", "313123"))
        self.wf._prepare_outbound_message = mock.MagicMock()
        self.wf._prepare_outbound_message.return_value = test_utilities.awaitable(("123", {"qwe": "qwe"}, "message"))
        wdo.set_outbound_status.return_value = test_utilities.awaitable(None)
        future = asyncio.Future()
        future.set_exception(httpclient.HTTPClientError(code=409))
        self.transmission.make_request.return_value = future

        error, text = await self.wf.handle_outbound_message(message_id="123",
                                                            correlation_id="qwe",
                                                            interaction_details={},
                                                            payload="nice message", work_description_object=None)

        wdo.set_outbound_status.assert_called_with(work_description.MessageStatus.OUTBOUND_MESSAGE_TRANSMISSION_FAILED)
        self.assertEqual(error, 500)
        self.assertEqual(text, 'Error(s) received from Spine: HTTP 409: Conflict')

    @mock.patch('mhs_common.state.work_description.create_new_work_description')
    @async_test
    async def test_send_message_http_status_code_err(self, wd_mock):
        wdo = mock.MagicMock()
        wdo.publish.return_value = test_utilities.awaitable(None)
        wd_mock.return_value = wdo
        self.wf._lookup_to_asid_details = mock.MagicMock()
        self.wf._lookup_to_asid_details.return_value = test_utilities.awaitable(("yes", "313123"))
        self.wf._prepare_outbound_message = mock.MagicMock()
        self.wf._prepare_outbound_message.return_value = test_utilities.awaitable(("123", {"qwe": "qwe"}, "message"))
        wdo.set_outbound_status.return_value = test_utilities.awaitable(None)
        response = mock.MagicMock()
        response.code = 400
        response.body = b'err response body'
        self.transmission.make_request.return_value = test_utilities.awaitable(response)

        error, text = await self.wf.handle_outbound_message(message_id="123",
                                                            correlation_id="qwe",
                                                            interaction_details={},
                                                            payload="nice message", work_description_object=None)

        wdo.set_outbound_status.assert_called_with(work_description.MessageStatus.OUTBOUND_MESSAGE_RESPONSE_RECEIVED)
        self.assertEqual(error, 400)
        self.assertEqual(text, 'err response body')

    @mock.patch('mhs_common.state.work_description.create_new_work_description')
    @async_test
    async def test_send_message_success_message(self, wd_mock):
        wdo = mock.MagicMock()
        wdo.publish.return_value = test_utilities.awaitable(None)
        wd_mock.return_value = wdo
        self.wf._lookup_to_asid_details = mock.MagicMock()
        self.wf._lookup_to_asid_details.return_value = test_utilities.awaitable(("yes", "313123"))
        self.wf._prepare_outbound_message = mock.MagicMock()
        self.wf._prepare_outbound_message.return_value = test_utilities.awaitable(("123", {"qwe": "qwe"}, "message"))
        wdo.set_outbound_status.return_value = test_utilities.awaitable(None)
        response = mock.MagicMock()
        response.code = 200
        response.body = b'response body'
        self.transmission.make_request.return_value = test_utilities.awaitable(response)

        error, text = await self.wf.handle_outbound_message(message_id="123",
                                                            correlation_id="qwe",
                                                            interaction_details={},
                                                            payload="nice message", work_description_object=None)

        wdo.set_outbound_status.assert_called_with(work_description.MessageStatus.OUTBOUND_MESSAGE_RESPONSE_RECEIVED)
        self.assertEqual(error, 200)
        self.assertEqual(text, 'response body')

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

    @mock.patch('mhs_common.messages.soap_envelope.SoapEnvelope.serialize')
    @async_test
    async def test_prepare_message_raises_exception(self, serialize_mock):
        serialize_mock.side_effect = Exception()
        with self.assertRaises(Exception):
            await self.wf._prepare_outbound_message("message_id", "to_asid", "from_asid", "mesasge",
                                                    {'service': 'service', 'action': 'action'})
