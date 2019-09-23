import abc
from typing import Dict

from tornado import httpclient


class TransmissionAdaptor(abc.ABC):

    @abc.abstractmethod
    async def make_request(self, url: str, headers: Dict[str, str], message: str,
                           raise_error_response: bool = True) -> httpclient.HTTPResponse:
        """Make a POST request to the given url, containing the provided message and HTTP headers. Raises an
        exception if a non-success HTTP status code is returned by the server.

        :param url: A string containing the url to send the request to.
        :param headers: A dictionary for the HTTP headers.
        :param message: The message body to send.
        :param raise_error_response: Return an error response
        :return: The tornado HTTPResponse object that represents the response of the object
        """
        pass
