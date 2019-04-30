from tornado.httpserver import HTTPServer
import tornado.ioloop
import tornado.web
from lxml import etree

response = """<?xml version="1.0" encoding="UTF-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/" xmlns:wsa="http://www.w3.org/2005/08/addressing" xmlns:wsu="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd" xmlns:wsse="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd">
	<soap:Header>
		<wsa:MessageID>3ACECEEA-6813-11E9-A60F-B7FB93FA902E</wsa:MessageID>
		<wsa:Action>urn:nhs-itk:services:201005:SendNHS111Report-v2-0Response</wsa:Action>
	</soap:Header>
	<soap:Body><itk:SimpleMessageResponse xmlns:itk="urn:nhs-itk:ns:201005">TEST_HARNESS_ID:7D6F23E0-AE1A-11DB-9808-B18E1E0994CD</itk:SimpleMessageResponse>
</soap:Body>
</soap:Envelope>"""


class MessageReceiver(tornado.web.RequestHandler):
    def initialize(self, servicesDict):
        pass

    def post(self):
        parser = etree.XMLParser(remove_blank_text=True)
        #print(etree.tostring(etree.fromstring(self.request.body), pretty_print=True).decode())
        root = etree.fromstring(self.request.body, parser)
        #print(etree.tostring(root, pretty_print=True).decode())
        self.write(response)

    def get(self):
        print("up and running boys")


if __name__ == "__main__":
    servicesDict = {}
    application = tornado.web.Application([(r"/syncsoap", MessageReceiver, dict(servicesDict=servicesDict))])

    httpsServer = HTTPServer(application)
    httpsServer.listen(4848)
    tornado.ioloop.IOLoop.instance().start()

