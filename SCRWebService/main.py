"""The main entry point for the summary care record service"""
import tornado.ioloop
import tornado.web
import utilities.integration_adaptors_logger as log
from scr import gp_summary_upload
from utilities import config, secrets, certs

import definitions
from endpoints import summary_care_record
from message_handling import message_forwarder, message_sender

logger = log.IntegrationAdaptorsLogger(__name__)


def build_app():
    interactions = {
        'SCR_GP_SUMMARY_UPLOAD': gp_summary_upload.GpSummaryUpload()
    }
    address = config.get_config('MHS_ADDRESS')

    certificates = certs.Certs.create_certs_files(definitions.ROOT_DIR,
                                                  ca_certs=secrets.get_secret_config('MHS_CA_CERTS', default=None))

    sender = message_sender.MessageSender(address, ca_certs=certificates.ca_certs_path)
    forwarder = message_forwarder.MessageForwarder(interactions, sender)

    app = tornado.web.Application([(r"/", summary_care_record.SummaryCareRecord, dict(forwarder=forwarder))])
    return app


def main():
    config.setup_config('SCR')
    secrets.setup_secret_config("SCR")
    log.configure_logging()
    app = build_app()
    scr_port = config.get_config('PORT', default='80')
    logger.info(f'Starting SCR web service on port {scr_port}')
    app.listen(int(scr_port))
    tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    try:
        main()
    except:
        logger.critical('Fatal exception in main application', exc_info=True)
    finally:
        logger.info('Exiting application')
