from typing import Dict
from utilities import integration_adaptors_logger as log
from tornado import httpclient

logger = log.IntegrationAdaptorsLogger("COMMON_HTTPS")


class CommonHttps:

    @staticmethod
    async def make_request(url: str, method: str, headers: Dict[str, str], body: str, client_cert: str = None,
                     client_key: str = None, ca_certs: str = None):
        logger.info("0001", "About to send {method} request with {headers} to {url} : {body}",
                    {"method": method, "headers": headers, "url": url, "body": body})
        response = await httpclient.AsyncHTTPClient().fetch(url=url,
                                                            method=method,
                                                            body=body,
                                                            headers=headers,
                                                            client_cert=client_cert,
                                                            client_key=client_key,
                                                            ca_certs=ca_certs,
                                                            validate_cert=True)
        logger.info("0002", "Sent {method} request with {headers} to {url} and received status code {code} : {body}",
                    {"method": method, "headers": headers, "url": url, "body": body, "code": response.code})
        return response
