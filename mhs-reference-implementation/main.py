from pathlib import Path

from utilities.file_utilities import FileUtilities

from definitions import ROOT_DIR
from mhs.builder.ebxml_request_message_builder import EbXmlRequestMessageBuilder
from mhs.config.interactions import InteractionsConfigFile
from mhs.sender.sender import Sender
from mhs.transport.http_transport import HttpTransport

# The ID of the interaction we're making a request for - ultimately this should come from the client's request
INTERACTION_NAME = 'gp_summary_upload'

data_dir = Path(ROOT_DIR) / "data"
certs_dir = str(data_dir / "certs")
interactions_config_file = str(data_dir / "interactions" / "interactions.json")

# Load HL7 message - ultimately this should come from the client's request
received_message = FileUtilities.get_file_string(str(data_dir / "messages" / "gp_summary_upload.xml"))

# Build the application
interactions_config = InteractionsConfigFile(interactions_config_file)
message_builder = EbXmlRequestMessageBuilder()
transport = HttpTransport(certs_dir)
sender = Sender(interactions_config, message_builder, transport)

# Send a request
response = sender.send_message(INTERACTION_NAME, received_message)
print(response)
