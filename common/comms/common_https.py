from typing import Dict

from tornado import httpclient

from utilities import integration_adaptors_logger as log

logger = log.IntegrationAdaptorsLogger("COMMON_HTTPS")


class CommonHttps(object):

    @staticmethod
    async def make_request(url: str, method: str, headers: Dict[str, str], body: str, client_cert: str = None,
                           client_key: str = None, ca_certs: str = None, validate_cert: bool = True,
                           http_proxy_host: str = None, http_proxy_port: int = None):
        """Send a HTTPS request and return it's response.
        :param url: A string containing the endpoint to send the request to.
        :param method: A string containing the HTTP method to send the request as.
        :param headers: A dictionary containing key value pairs for the details of the HTTP header.
        :param body: A string containing the message to send to the endpoint.
        :param client_cert: A string containing the full path of the client certificate file.
        :param client_key: A string containing the full path of the client private key file.
        :param ca_certs: A string containing the full path of the certificate authority certificate file.
        :param validate_cert: Whether the server's certificate should be validated or not.
        :param http_proxy_host The hostname of the HTTP proxy to be used.
        :param http_proxy_port The port of the HTTP proxy to be used.
        """

        logger.info("0001", "About to send {method} request with {headers} to {url} using {proxy_host} & {proxy_port}",
                    {"method": method, "headers": headers, "url": url, "proxy_host": http_proxy_host,
                     "proxy_port": http_proxy_port})

        if not validate_cert:
            logger.warning("0003", "Server certificate validation has been disabled.")

        response = await httpclient.AsyncHTTPClient().fetch(url,
                                                            method=method,
                                                            body=body,
                                                            headers=headers,
                                                            client_cert=client_cert,
                                                            client_key=client_key,
                                                            ca_certs=ca_certs,
                                                            validate_cert=validate_cert,
                                                            proxy_host=http_proxy_host,
                                                            proxy_port=http_proxy_port)
        logger.info("0002",
                    "Sent {method} request with {headers} to {url} using {proxy_host} & {proxy_port}, and "
                    "received status code {code}",
                    {"method": method, "headers": headers, "url": url, "proxy_host": http_proxy_host,
                     "proxy_port": http_proxy_port, "code": response.code})
        return response
