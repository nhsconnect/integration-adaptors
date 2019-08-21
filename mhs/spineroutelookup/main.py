import tornado.httpserver
import tornado.ioloop
import tornado.web
from utilities import config
from utilities import integration_adaptors_logger as log

from request import handler

logger = log.IntegrationAdaptorsLogger('SPINE_ROUTE_LOOKUP_MAIN')


def start_tornado_server() -> None:
    """
    Start the Tornado server
    """
    application = tornado.web.Application([(".*", handler.RoutingDirectoryRequestHandler)])
    server = tornado.httpserver.HTTPServer(application)
    server.listen(443)

    logger.info('003', 'Starting server')
    tornado.ioloop.IOLoop.current().start()


def main():
    config.setup_config("MHS")
    log.configure_logging()

    start_tornado_server()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.critical('001', 'Fatal exception in main application: {exception}', {'exception': e})
    finally:
        logger.info('002', 'Exiting application')
