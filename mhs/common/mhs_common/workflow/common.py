"""This module defines the common base of all workflows."""
import abc
from typing import Tuple, AnyStr
from xml.etree import ElementTree

from tornado import httpclient
from utilities.integration_adaptors_logger import IntegrationAdaptorsLogger

import mhs_common.state.work_description as wd
from mhs_common.messages.soap_fault import SOAPFault


class CommonWorkflow(abc.ABC):
    """Common functionality across all workflows."""

    @abc.abstractmethod
    async def handle_outbound_message(self, message_id: str, correlation_id: str, interaction_details: dict,
                                      payload: str) -> Tuple[int, str]:
        """
        Handle a message from the supplier system (or a message from an adaptor that the supplier system speaks to)
        that is to be sent outbound.

        :param message_id: ID of the message to send
        :param correlation_id: correlation ID of the request
        :param interaction_details: interaction details used to construct the message to send outbound
        :param payload: payload to send outbound
        :return: the HTTP status and body to return as a response
        """
        pass

    @abc.abstractmethod
    async def handle_inbound_message(self, message_id: str, correlation_id: str, work_description: wd.WorkDescription,
                                     payload: str):
        """
        Handles an inbound message from an external system (typically from spine)

        :param message_id: ID of the message the original request to Spine was made with
        :param correlation_id: correlation ID of the request
        :param work_description: work description object for the payload
        :param payload: payload to handle
        """
        pass

    @staticmethod
    def handle_spine_fault(error: httpclient.HTTPClientError,
                           logger: IntegrationAdaptorsLogger) -> Tuple[int, AnyStr]:
        """

        :param error: Tornado's HTTPClient error instance
        :param logger: Logger to be used to log Spine error(s)
        :return: Response to external client represented as HTTP status code and body
        """
        response_code = error.response.code
        response_headers = error.response.headers
        response_body = error.response.body
        client_message = 'Error(s) returned from Spine. Contact system administrator.'

        if response_code == 500:
            assert 'Content-Type' in response_headers
            if response_headers['Content-Type'] == 'text/xml':
                parsed_body = ElementTree.fromstring(response_body)

                if SOAPFault.is_soap_fault(parsed_body):
                    fault: SOAPFault = SOAPFault.from_parsed(response_headers, parsed_body)

                    for error in fault.error_list:
                        err_text = ', '.join([f'{k}={v}' for k, v in error.items()])
                        logger.error(f'Error from Spine: {err_text}', '0010')

        return 500, client_message
