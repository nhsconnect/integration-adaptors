from typing import Optional, Awaitable

from tornado.httpserver import HTTPServer
import tornado.ioloop
import tornado.web

from reciever.message_checks.checks import *
from utilities.file_utilities import FileUtilities
from definitions import XML_PATH
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

        self.set_status(mh.get_response_code())
        logging.debug("Status code %i", mh.get_response_code())

        logging.debug("Sending reply")
        self.write(mh.get_response())


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    application = tornado.web.Application([(r"/syncsoap", MessageReceiver)])

    httpsServer = HTTPServer(application)
    httpsServer.listen(4848)
    tornado.ioloop.IOLoop.current().start()
