import os
import tornado.web
import tornado.ioloop
from utilities import config
from endpoints import gp_summary_upload
import utilities.integration_adaptors_logger as log


if __name__ == "__main__":
    log.configure_logging()
    logger = log.IntegrationAdaptorsLogger('SCR-WEB')
    config.setup_config('SCR')

    app = tornado.web.Application([(r"/gp_summary_upload", gp_summary_upload.GpSummaryUpload)])
    app.listen(80)
    tornado.ioloop.IOLoop.current().start()
