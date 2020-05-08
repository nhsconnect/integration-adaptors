import pathlib
import ssl
from typing import Dict

import definitions
import tornado.httpserver
import tornado.ioloop
import tornado.web
import utilities.config as config
import utilities.integration_adaptors_logger as log
from comms import proton_queue_adaptor
from mhs_common import workflow
from mhs_common.configuration import configuration_manager
from handlers import healthcheck_handler
from persistence import persistence_adaptor
from persistence.persistence_adaptor_factory import get_persistence_adaptor
from utilities import secrets, certs

import inbound.request.handler as async_request_handler
from utilities.string_utilities import str2bool

logger = log.IntegrationAdaptorsLogger(__name__)

ASYNC_TIMEOUT = 30

config.setup_config("MHS")
secrets.setup_secret_config("MHS")
log.configure_logging("inbound")


def build_ssl_context(local_certs_file: str, ca_certs_file: str, key_file: str, ):
    """
    :param local_certs_file: The filename of the certificate to present for authentication.
    :param ca_certs_file: The filename of the CA certificates as passed to ssl.SSLContext.load_verify_locations
    :param key_file: The filename of the private key for the certificate identified by local_certs_file.
    """
    # Ensure Client authentication
    ssl_ctx = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    ssl_ctx.load_cert_chain(local_certs_file, key_file)
    # The docs suggest we have to specify both that we must verify the client cert and the locations
    ssl_ctx.verify_mode = ssl.CERT_REQUIRED
    ssl_ctx.load_verify_locations(ca_certs_file)

    return ssl_ctx


def start_inbound_server(local_certs_file: str, ca_certs_file: str, key_file: str, party_key: str,
                         workflows: Dict[str, workflow.CommonWorkflow],
                         persistence_store: persistence_adaptor.PersistenceAdaptor,
                         config_manager: configuration_manager.ConfigurationManager
                         ) -> None:
    """
    :param persistence_store: persistence store adaptor for message information
    :param local_certs_file: The filename of the certificate to present for authentication.
    :param ca_certs_file: The filename of the CA certificates as passed to ssl.SSLContext.load_verify_locations
    :param key_file: The filename of the private key for the certificate identified by local_certs_file.
    :param workflows: The workflows to be used to handle messages.
    :param config_manager: The config manager used to obtain interaction details
    :param party_key: The party key to use to identify this MHS.
    """

    inbound_application = tornado.web.Application(
        [(r"/.*", async_request_handler.InboundHandler, dict(workflows=workflows, party_id=party_key,
                                                             work_description_store=persistence_store,
                                                             config_manager=config_manager))])

    ssl_ctx = build_ssl_context(local_certs_file, ca_certs_file, key_file) \
        if str2bool(config.get_config('INBOUND_USE_SSL', default=str(True))) \
        else None

    inbound_server = tornado.httpserver.HTTPServer(inbound_application, ssl_options=ssl_ctx)
    inbound_server_port = int(config.get_config('INBOUND_SERVER_PORT', default='443'))
    inbound_server.listen(inbound_server_port)

    healthcheck_application = tornado.web.Application([
        ("/healthcheck", healthcheck_handler.HealthcheckHandler)
    ])
    healthcheck_server_port = int(config.get_config('INBOUND_HEALTHCHECK_SERVER_PORT', default='80'))
    healthcheck_application.listen(healthcheck_server_port)

    logger.info('Starting inbound server at port {server_port} and healthcheck at {healthcheck_server_port}',
                fparams={'server_port': inbound_server_port, 'healthcheck_server_port': healthcheck_server_port})
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


def create_queue_adaptor():
    return proton_queue_adaptor.ProtonQueueAdaptor(
        urls=config.get_config('INBOUND_QUEUE_BROKERS').split(','),
        queue=config.get_config('INBOUND_QUEUE_NAME'),
        username=secrets.get_secret_config('INBOUND_QUEUE_USERNAME', default=None),
        password=secrets.get_secret_config('INBOUND_QUEUE_PASSWORD', default=None),
        max_retries=int(config.get_config('INBOUND_QUEUE_MAX_RETRIES', default='3')),
        retry_delay=int(config.get_config('INBOUND_QUEUE_RETRY_DELAY', default='100')) / 1000,
        ttl_in_seconds=int(config.get_config('INBOUND_QUEUE_MESSAGE_TTL_IN_SECONDS', default='0')))


def create_sync_async_store():
    return get_persistence_adaptor(
        table_name=config.get_config('SYNC_ASYNC_STATE_TABLE_NAME'),
        max_retries=int(config.get_config('SYNC_ASYNC_STORE_MAX_RETRIES', default='3')),
        retry_delay=int(config.get_config('SYNC_ASYNC_STORE_RETRY_DELAY', default='100')) / 1000)


def create_work_description_store():
    return get_persistence_adaptor(
        table_name=config.get_config('STATE_TABLE_NAME'),
        max_retries=int(config.get_config('STATE_STORE_MAX_RETRIES', default='3')),
        retry_delay=int(config.get_config('STATE_STORE_RETRY_DELAY', default='100')) / 1000)


def main():
    certificates = certs.Certs.create_certs_files(definitions.ROOT_DIR,
                                                  private_key=secrets.get_secret_config('CLIENT_KEY'),
                                                  local_cert=secrets.get_secret_config('CLIENT_CERT'),
                                                  ca_certs=secrets.get_secret_config('CA_CERTS'))
    party_key = secrets.get_secret_config('PARTY_KEY')

    queue_adaptor = create_queue_adaptor()
    work_description_store = create_work_description_store()
    sync_async_store = create_sync_async_store()

    workflows = workflow.get_workflow_map(inbound_async_queue=queue_adaptor,
                                          work_description_store=work_description_store,
                                          sync_async_store=sync_async_store)

    interactions_config_file = pathlib.Path(definitions.ROOT_DIR) / 'data' / "interactions" / "interactions.json"
    config_manager = configuration_manager.ConfigurationManager(str(interactions_config_file))

    start_inbound_server(certificates.local_cert_path, certificates.ca_certs_path, certificates.private_key_path,
                         party_key, workflows, work_description_store, config_manager)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        logger.critical('Fatal exception in main application', exc_info=True)
    finally:
        logger.info('Exiting application')
