from tornado.httpserver import HTTPServer
import tornado.ioloop
import tornado.web
from lxml import etree
import xml.etree.ElementTree as ET

response = """<?xml version="1.0" encoding="UTF-8"?>
    <soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/" xmlns:wsa="http://www.w3.org/2005/08/addressing" xmlns:wsu="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd" xmlns:wsse="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd">
        <soap:Header>
            <wsa:MessageID>3ACECEEA-6813-11E9-A60F-B7FB93FA902E</wsa:MessageID>
            <wsa:Action>urn:nhs-itk:services:201005:SendNHS111Report-v2-0Response</wsa:Action>
        </soap:Header>
        <soap:Body><itk:SimpleMessageResponse xmlns:itk="urn:nhs-itk:ns:201005">TEST_HARNESS_ID:7D6F23E0-AE1A-11DB-9808-B18E1E0994CD</itk:SimpleMessageResponse>
    </soap:Body>
    </soap:Envelope>
    
"""

wrong_service_body = """<?xml version="1.0" encoding="UTF-8"?>
    <soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/" xmlns:wsa="http://www.w3.org/2005/08/addressing" xmlns:wsu="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd" xmlns:wsse="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd">
        <soap:Header>
            <wsa:MessageID>79EBC3D8-6BFE-11E9-B1E7-EB711959C3B2</wsa:MessageID>
            <wsa:Action>http://www.w3.org/2005/08/addressing/soap/fault</wsa:Action>
        </soap:Header>
        <soap:Body><soap:Fault xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
        <faultcode>Client</faultcode>
        <faultstring>ATM A client related error has occurred, see detail element for further information</faultstring>
        <detail>
            <toolkit:ToolkitErrorInfo xmlns:toolkit="urn:nhs-itk:ns:201005">
                <toolkit:ErrorID>79E952D7-6BFE-11E9-B1E7-EB711959C3B2</toolkit:ErrorID>
                <toolkit:ErrorCode>1000</toolkit:ErrorCode>
                <toolkit:ErrorText>Invalid message</toolkit:ErrorText>
                <toolkit:ErrorDiagnosticText>Test message rejection. TEST_HARNESS_ID:7D6F23E0-AE1A-11DB-9808-B18E1E0994CD</toolkit:ErrorDiagnosticText>
            </toolkit:ToolkitErrorInfo>
        </detail>
    </soap:Fault>
    </soap:Body>
    </soap:Envelope>
    
"""


class MessageHandler:

    @staticmethod
    def check_action_types(tree):
        pass


    @staticmethod
    def evaluate_message(xml_string):
        tree = ET.fromstring(xml_string)
        namespaces = {
            'soap': 'http://schemas.xmlsoap.org/soap/envelope/',
            'a': 'http://www.etis.fskab.se/v1.0/ETISws',
            'wsa': 'http://www.w3.org/2005/08/addressing',
            'itk': 'urn:nhs-itk:ns:201005'
        }

        header_action = ""
        for type_tag in tree.findall("./soap:Header"
                                     "/wsa:Action",
                                        namespaces):
            header_action = type_tag.text

        body_service = ""
        for type_tag in tree.findall('./soap:Body'
                                     '/itk:DistributionEnvelope'
                                     '/itk:header',
                                     namespaces):
            body_service = type_tag.attrib['service']

        print(body_service)
        if header_action != body_service:
            return 500, wrong_service_body

        return 200, response


class MessageReceiver(tornado.web.RequestHandler):
    def initialize(self, servicesDict):
        pass

    def post(self):
       # parser = etree.XMLParser(remove_blank_text=True)
       # root = etree.fromstring(self.request.body, parser)
       # print(etree.tostring(root, pretty_print=True).decode())

        status_code, message_response = MessageHandler.evaluate_message(self.request.body)
        self.set_status(status_code)
        self.write(message_response)
       ##self.finish()
        #self.flush(True)
        #self.finish(message_response)
        print("Responded")

    def get(self):
        print("Test get method")


if __name__ == "__main__":
    servicesDict = {}
    application = tornado.web.Application([(r"/syncsoap", MessageReceiver, dict(servicesDict=servicesDict))], debug=True)

    httpsServer = HTTPServer(application)
    httpsServer.listen(4848)
    tornado.ioloop.IOLoop.instance().start()
