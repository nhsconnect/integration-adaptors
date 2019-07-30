import os
import json

import tornado.web
import tornado.ioloop
import scr.gp_summary_update as scr_update
import utilities.integration_adaptors_logger as log

logger = log.IntegrationAdaptorsLogger('SCR_WEB')


class GpSummaryUpload(tornado.web.RequestHandler):

    def _initialize(self) -> None:
        self.mhs_address = os.environ['MHS_ADDRESS']
        assert self.mhs_address

    def post(self):
        """
        Receives a json payload and attempts to populate a gp summary upload message, for testing purposes 
        this end point currently returns the data provided  
        :return:
        """
        
        try:
            scr_input_json = json.loads(self.request.body)
        except json.decoder.JSONDecodeError:
            self.set_status(500)
            return self.write("Empty body received with post request")
            
        try:
            summary_care_record = scr_update.SummaryCareRecord()
            hl7_message = summary_care_record.populate_template(scr_input_json)
            logger.info("0100", hl7_message)
            self.write(scr_input_json)
        except Exception as e:
            logger.error('0200', f'Summary care message generation failed: {e}')
            self.set_status(500)
            self.write('Exception raised whilst populating hl7 message with json')

