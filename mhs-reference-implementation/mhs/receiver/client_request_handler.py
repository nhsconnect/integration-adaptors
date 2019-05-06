from tornado.web import RequestHandler

# The ID of the interaction we're making a request for - ultimately this should come from the client's request
from utilities.file_utilities import FileUtilities

INTERACTION_NAME = 'gp_summary_upload'


class ClientRequestHandler(RequestHandler):
    """A RequestHandler for client requests to this MHS."""

    def initialize(self, data_dir, sender):
        """Initialise this request handler with the provided configuration values.

        :param data_dir: The directory to load messages from
        :param sender: The sender to use to send messages.
        :return:
        """
        # Load HL7 message - ultimately this should come from the client's request
        self.message = FileUtilities.get_file_string(str(data_dir / "messages" / "gp_summary_upload.xml"))
        self.sender = sender

    def post(self):
        print(f"Client POST received: {self.request}")

        response = self.sender.send_message(INTERACTION_NAME, self.message)
        print(f"Message sent. Received response: {response}")

        self.write("Message sent.")
