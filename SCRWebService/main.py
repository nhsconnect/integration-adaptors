"""The main entry point for the summary care record service"""
import tornado.web
import tornado.ioloop
from utilities import config
from endpoints import summary_care_record
import utilities.integration_adaptors_logger as log
from message_handling import message_forwarder
from scr import gp_summary_update

logger = log.IntegrationAdaptorsLogger('SCR-WEB')


def main():
    config.setup_config('SCR')
    log.configure_logging()
    interactions = {
        'SCR_GP_SUMMARY_UPLOAD': gp_summary_update.SummaryCareRecord()
    }
    forwarder = message_forwarder.MessageForwarder(interactions)

    app = tornado.web.Application([(r"/", summary_care_record.SummaryCareRecord, dict(forwarder=forwarder))])
    app.listen(80)
    tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.critical('001', 'Fatal exception in main application: {exception}', {'exception': e})
    finally:
        logger.info('002', 'Exiting application')

