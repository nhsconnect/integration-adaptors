import os
import json
import tornado.web
import tornado.ioloop
import scr.gp_summary_update as scr_update
import utilities.integration_adaptors_logger as log

logger = log.IntegrationAdaptorsLogger('GP_SUM_UP')


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
        except json.decoder.JSONDecodeError as e:
            self.set_status(500)
            logger.error('001', f'Failed to parse message body: {e}')
            return self.write(f'Failed to parse message body: {e}')

        try:
            scr = scr_update.SummaryCareRecord()
            hl7 = scr.populate_template(scr_input_json)
            logger.info("002", hl7)
            self.write(scr_input_json)
        except Exception as e:
            self.set_status(500)
            logger.error('003', f'Summary care message generation failed: {e}')
            return self.write(f'Exception raised whilst populating hl7 message with json: {e}')

