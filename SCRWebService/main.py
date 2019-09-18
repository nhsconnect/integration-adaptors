import os
import tornado.web
import tornado.ioloop
from utilities import config
from endpoints import gp_summary_upload
import utilities.integration_adaptors_logger as log


if __name__ == "__main__":
    config.setup_config('SCR')
    log.configure_logging()
    logger = log.IntegrationAdaptorsLogger('SCR-WEB')

    app = tornado.web.Application([(r"/gp_summary_upload", gp_summary_upload.SummaryCareRecord)])
    app.listen(80)
    tornado.ioloop.IOLoop.current().start()
