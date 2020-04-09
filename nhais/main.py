import tornado.httpclient
import utilities.integration_adaptors_logger as log
from requests import healthcheck_handler
from utilities import config
from outbound.request import handler

logger = log.IntegrationAdaptorsLogger(__name__)

def configure_http_client():
    """
    Configure Tornado to use the curl HTTP client.
    """
    tornado.httpclient.AsyncHTTPClient.configure('tornado.curl_httpclient.CurlAsyncHTTPClient')

def start_tornado_server() -> None:

    supplier_application = tornado.web.Application(
        [
            (r'/fhir/Patient/.*', handler.Handler),
            (r'/healthcheck', healthcheck_handler.HealthcheckHandler)
        ])
    supplier_server = tornado.httpserver.HTTPServer(supplier_application)
    server_port = int(config.get_config('SERVER_PORT', default='80'))
    supplier_server.listen(server_port)

    logger.info('Starting nhais server at port {server_port}', fparams={'server_port': server_port})
    tornado_io_loop = tornado.ioloop.IOLoop.current()
    try:
        tornado_io_loop.start()
    except KeyboardInterrupt:
        logger.warning('Keyboard interrupt')
        pass
    finally:
        tornado_io_loop.stop()
        tornado_io_loop.close(True)
    logger.info('Server shut down, exiting...')

def main():
    config.setup_config("NHAIS")
    log.configure_logging("NHAIS")

    configure_http_client()
    logger.info('Starting tornado server')
    start_tornado_server()

if __name__ == "__main__":
    try:
        main()
    except Exception:
        logger.critical('Fatal exception in main application', exc_info=True)
    finally:
        logger.info('Exiting application')