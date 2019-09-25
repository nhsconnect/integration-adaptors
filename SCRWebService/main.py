"""The main entry point for the summary care record service"""
import tornado.web
import tornado.ioloop
from utilities import config
from endpoints import summary_care_record
import utilities.integration_adaptors_logger as log
from message_handling import message_forwarder, message_sender
from scr import gp_summary_upload

logger = log.IntegrationAdaptorsLogger('SCR-WEB')


def build_app():
    interactions = {
        'SCR_GP_SUMMARY_UPLOAD': gp_summary_upload.GpSummaryUpload()
    }
    address = 'http://' + config.get_config('MHS_ADDRESS') + '/'
    sender = message_sender.MessageSender(address)
    forwarder = message_forwarder.MessageForwarder(interactions, sender)

    app = tornado.web.Application([(r"/", summary_care_record.SummaryCareRecord, dict(forwarder=forwarder))])
    return app


def main():
    config.setup_config('SCR')
    log.configure_logging()
    app = build_app()
    app.listen(80)
    tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.critical('001', 'Fatal exception in main application: {exception}', {'exception': e})
    finally:
        logger.info('002', 'Exiting application')

