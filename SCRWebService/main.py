import os
import tornado.web
import tornado.ioloop
from utilities import config
from endpoints import gp_summary_upload
import utilities.integration_adaptors_logger as log


if __name__ == "__main__":
    logger = log.IntegrationAdaptorsLogger('SCR-WEB')
    config.setup_config('SCR')
    log.configure_logging()

    app = tornado.web.Application([(r"/gpsummaryupload", gp_summary_upload.GpSummaryUpload)])
    app.listen(80)
    tornado.ioloop.IOLoop.current().start()
