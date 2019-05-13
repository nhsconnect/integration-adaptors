from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
import tornado.web

from reciever.message_checks.checks import *
from utilities.file_utilities import FileUtilities
from OneOneOne.definitions import XML_PATH
from OneOneOne.reciever.message_handler import MessageHandler

response = FileUtilities.get_file_string(XML_PATH / 'basic_success_response.xml')

check_list = [CheckManifestCountInstances, CheckActionTypes, CheckManifestPayloadCounts,
              CheckPayloadCountAgainstActual, CheckPayloadIdAgainstManifestId
              ]


class MessageReceiver(tornado.web.RequestHandler):

    def initialize(self, servicesdict=None):
        pass

    def post(self):
        logging.debug("Post message received ")
        mh = MessageHandler(self.request.body)

        status_code = self.get_status_code(mh.error_flag)
        self.set_status(status_code)
        logging.debug("Status code %i", status_code)

        logging.debug("Sending reply")
        self.write(mh.get_response())

    def get_status_code(self, flag):
        if flag:
            return 500
        else:
            return 200


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    application = tornado.web.Application([(r"/syncsoap", MessageReceiver)])

    httpsServer = HTTPServer(application)
    httpsServer.listen(4848)
    IOLoop.current().start()
