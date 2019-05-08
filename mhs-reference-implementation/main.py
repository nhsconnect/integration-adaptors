import logging
from pathlib import Path
import ssl

from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from tornado.web import Application

from definitions import ROOT_DIR
from mhs.builder.ebxml_ack_message_builder import EbXmlAckMessageBuilder
from mhs.builder.ebxml_request_message_builder import EbXmlRequestMessageBuilder
from mhs.config.interactions import InteractionsConfigFile
from mhs.handler.async_response_handler import AsyncResponseHandler
from mhs.handler.client_request_handler import ClientRequestHandler
from mhs.parser.ebxml_message_parser import EbXmlRequestMessageParser
from mhs.sender.sender import Sender
from mhs.transport.http_transport import HttpTransport

data_dir = Path(ROOT_DIR) / "data"
certs_dir = data_dir / "certs"
certs_file = str(certs_dir / "client.pem")
key_file = str(certs_dir / "client.key")
interactions_config_file = str(data_dir / "interactions" / "interactions.json")

# Build the application
interactions_config = InteractionsConfigFile(interactions_config_file)
message_builder = EbXmlRequestMessageBuilder()
transport = HttpTransport(str(certs_dir))
sender = Sender(interactions_config, message_builder, transport)

ack_builder = EbXmlAckMessageBuilder()
message_parser = EbXmlRequestMessageParser()

# Configure logging
logging.basicConfig(format="%(asctime)s - %(levelname)s: %(message)s", level=logging.DEBUG)

# Run the Tornado server
supplier_application = Application([(r"/send", ClientRequestHandler, dict(data_dir=data_dir, sender=sender))])
supplier_server = HTTPServer(supplier_application)
supplier_server.listen(80)

mhs_application = Application([
    (r".*", AsyncResponseHandler, dict(ack_builder=ack_builder, message_parser=message_parser))
])
mhs_server = HTTPServer(mhs_application,
                        ssl_options=dict(certfile=certs_file, keyfile=key_file, cert_reqs=ssl.CERT_REQUIRED,
                                         ca_certs=certs_file))
mhs_server.listen(443)

logging.info("Starting servers")
IOLoop.current().start()
