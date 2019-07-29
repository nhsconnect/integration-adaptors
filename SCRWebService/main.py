import json
import os
import tornado.ioloop
import tornado.web
import scr.gp_summary_update as scr_update
import utilities.integration_adaptors_logger as log

logger = log.IntegrationAdaptorsLogger('SCR-WEB')


class SCRReciever(tornado.web.RequestHandler):

    def _initialize(self) -> None:
        self.mhs_address = os.environ['MHS_ADDRESS']
        assert self.mhs_address
        print(self.mhs_address)

    def post(self):
        scr_input_hash = json.loads(self.request.body)
        try:
            summary_care_record = scr_update.SummaryCareRecord()
            hl7_message = summary_care_record.populate_template(scr_input_hash)
            logger.info("0200", hl7_message)
            self.write(scr_input_hash)
        except Exception as e:
            logger.error('0100', f'Summary care message generation failed: {e}')
            self.set_status(500)
            self.write('Exception raised whilst populating hl7 message with json')


if __name__ == "__main__":

    app = tornado.web.Application([(r"/scr", SCRReciever)])
    app.listen(9000)
    tornado.ioloop.IOLoop.current().start()
    print("Server started")