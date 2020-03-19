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
from mhs_common.request import healthcheck_handler
from mhs_common.state import persistence_adaptor, dynamo_persistence_adaptor
from utilities import secrets, certs

import inbound.request.handler as async_request_handler

logger = log.IntegrationAdaptorsLogger('INBOUND_MAIN')

ASYNC_TIMEOUT = 30


def initialise_workflows() -> Dict[str, workflow.CommonWorkflow]:
    """Initialise the workflows
    :return: The workflows that can be used to handle messages.
    """

    queue_adaptor = proton_queue_adaptor.ProtonQueueAdaptor(
        host=config.get_config('INBOUND_QUEUE_URL'),
        username=secrets.get_secret_config('INBOUND_QUEUE_USERNAME'),
        password=secrets.get_secret_config('INBOUND_QUEUE_PASSWORD'))
    raw_queue_adaptor = proton_queue_adaptor.ProtonQueueAdaptor(
        host=config.get_config('INBOUND_RAW_QUEUE_URL'),
        username=secrets.get_secret_config('INBOUND_QUEUE_USERNAME'),
        password=secrets.get_secret_config('INBOUND_QUEUE_PASSWORD'))
    sync_async_store = dynamo_persistence_adaptor.DynamoPersistenceAdaptor(
        table_name=config.get_config('SYNC_ASYNC_STATE_TABLE_NAME'))

    inbound_queue_max_retries = int(config.get_config('INBOUND_QUEUE_MAX_RETRIES', default='3'))
    inbound_queue_retry_delay = int(config.get_config('INBOUND_QUEUE_RETRY_DELAY', default='100'))
    persistence_store_max_retries = int(config.get_config('STATE_STORE_MAX_RETRIES', default='3'))
    sync_async_delay = int(config.get_config('SYNC_ASYNC_STORE_RETRY_DELAY', default='100'))
    work_description_store = dynamo_persistence_adaptor.DynamoPersistenceAdaptor(
        table_name=config.get_config('STATE_TABLE_NAME'))
    return workflow.get_workflow_map(raw_queue_adaptor=raw_queue_adaptor,
                                     inbound_async_queue=queue_adaptor,
                                     work_description_store=work_description_store,
                                     sync_async_store=sync_async_store,
                                     persistence_store_max_retries=persistence_store_max_retries,
                                     sync_async_store_retry_delay=sync_async_delay,
                                     inbound_queue_max_retries=inbound_queue_max_retries,
                                     inbound_queue_retry_delay=inbound_queue_retry_delay
                                     )


def start_inbound_server(local_certs_file: str, ca_certs_file: str, key_file: str, party_key: str,
                         workflows: Dict[str, workflow.CommonWorkflow],
                         persistence_store: persistence_adaptor.PersistenceAdaptor,
                         config_manager: configuration_manager.ConfigurationManager
                         ) -> None:
    """

    :param persistence_store: persistence store adaptor for message information
    :param local_certs_file: The filename of the certificate to present for authentication.
    :param ca_certs_file: The filename of the CA certificates as passed to
    ssl.SSLContext.load_verify_locations
    :param key_file: The filename of the private key for the certificate identified by local_certs_file.
    :param workflows: The workflows to be used to handle messages.
    :param config_manager: The config manager used to obtain interaction details
    :param party_key: The party key to use to identify this MHS.
    """

    handlers = [(r"/.*", async_request_handler.InboundHandler, dict(workflows=workflows, party_id=party_key,
                                                             work_description_store=persistence_store,
                                                             config_manager=config_manager))]
    healthcheck_endpoint = ("/healthcheck", healthcheck_handler.HealthcheckHandler)

    # Ensure Client authentication
    if not config.get_config('NO_TLS', default='False') == 'True':
        ssl_ctx = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        ssl_ctx.load_cert_chain(local_certs_file, key_file)
        # The docs suggest we have to specify both that we must verify the client cert and the locations
        ssl_ctx.verify_mode = ssl.CERT_REQUIRED
        ssl_ctx.load_verify_locations(ca_certs_file)

        inbound_server = tornado.httpserver.HTTPServer(tornado.web.Application(handlers), ssl_options=ssl_ctx)
        inbound_server.listen(443)
        logger.info('011', 'Started main handler listener at 443')
        # Start health check on port 80
        healthcheck_application = tornado.web.Application([healthcheck_endpoint])
        healthcheck_application.listen(80)
        logger.info('011', 'Started health check listener at 80')
    else:
        # Add health check endpoint
        handlers.insert(0, healthcheck_endpoint)
        inbound_server = tornado.httpserver.HTTPServer(tornado.web.Application(handlers))
        inbound_server.listen(80)
        logger.info('011', 'Started main handler and health check listener at 80')


    logger.info('011', 'Starting inbound server')
    tornado.ioloop.IOLoop.current().start()


def main():
    config.setup_config("MHS")
    secrets.setup_secret_config("MHS")
    log.configure_logging()

    if config.get_config('NO_TLS', default='False') == 'True':
        certificates = certs.Certs()
    else:
        certificates = certs.Certs.create_certs_files(definitions.ROOT_DIR,
                                                      private_key=secrets.get_secret_config('CLIENT_KEY'),
                                                      local_cert=secrets.get_secret_config('CLIENT_CERT'),
                                                      ca_certs=secrets.get_secret_config('CA_CERTS'))

    party_key = secrets.get_secret_config('PARTY_KEY')

    workflows = initialise_workflows()
    store = dynamo_persistence_adaptor.DynamoPersistenceAdaptor(table_name=config.get_config('STATE_TABLE_NAME'))

    interactions_config_file = pathlib.Path(definitions.ROOT_DIR) / 'data' / "interactions" / "interactions.json"
    config_manager = configuration_manager.ConfigurationManager(str(interactions_config_file))

    start_inbound_server(certificates.local_cert_path, certificates.ca_certs_path, certificates.private_key_path,
                         party_key, workflows, store, config_manager)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.critical('001', 'Fatal exception in main application: {exception}', {'exception': e})
    finally:
        logger.info('002', 'Exiting application')
