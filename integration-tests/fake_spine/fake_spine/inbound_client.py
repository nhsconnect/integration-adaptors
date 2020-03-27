import logging

from tornado import httpclient

from fake_spine import config
from fake_spine.spine_responses import InboundRequest

logger = logging.getLogger(__name__)

class InboundClient(object):

    HEADERS = {
        'Content-Type': 'multipart/related; boundary="--=_MIME-Boundary"; charset="UTF-8"; type="text/xml"; '
                        'start="<ebXMLHeader@spine.nhs.uk>"'
    }

    def __init__(self):
        self.http_client = httpclient.AsyncHTTPClient()
        self.inbound_url = f'http://localhost:{config.INBOUND_PROXY_PORT}/inbound-proxy'

    async def make_request(self, request: InboundRequest):
        logger.info(f'Making inbound request to {self.inbound_url}')
        response = await self.http_client.fetch(self.inbound_url,
                                                method='POST',
                                                body=request.body,
                                                raise_error=True,
                                                headers={**self.HEADERS, **request.headers})
        return response
