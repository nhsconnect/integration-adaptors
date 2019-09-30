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
    sync_async_store = dynamo_persistence_adaptor.DynamoPersistenceAdaptor(
        table_name=config.get_config('SYNC_ASYNC_STATE_TABLE_NAME'))

    inbound_queue_max_retries = int(config.get_config('INBOUND_QUEUE_MAX_RETRIES', default='3'))
    inbound_queue_retry_delay = int(config.get_config('INBOUND_QUEUE_RETRY_DELAY', default='100'))
    persistence_store_max_retries = int(config.get_config('STATE_STORE_MAX_RETRIES', default='3'))
    sync_async_delay = int(config.get_config('SYNC_ASYNC_STORE_RETRY_DELAY', default='100'))
    return workflow.get_workflow_map(inbound_async_queue=queue_adaptor,
                                     sync_async_store=sync_async_store,
                                     persistence_store_max_retries=persistence_store_max_retries,
                                     sync_async_store_retry_delay=sync_async_delay,
                                     inbound_queue_max_retries=inbound_queue_max_retries,
                                     inbound_queue_retry_delay=inbound_queue_retry_delay
                                     )


def start_inbound_server(local_certs_file: str, ca_certs_file: str, key_file: str, party_key: str,
                         workflows: Dict[str, workflow.CommonWorkflow],
                         persistence_store: persistence_adaptor.PersistenceAdaptor
                         ) -> None:
    """

    :param persistence_store: persistence store adaptor for message information
    :param local_certs_file: The filename of the certificate to present for authentication.
    :param ca_certs_file: The filename of the CA certificates as passed to
    ssl.SSLContext.load_verify_locations
    :param key_file: The filename of the private key for the certificate identified by local_certs_file.
    :param workflows: The workflows to be used to handle messages.
    :param party_key: The party key to use to identify this MHS.
    """

    inbound_application = tornado.web.Application(
        [(r"/.*", async_request_handler.InboundHandler, dict(workflows=workflows, party_id=party_key,
                                                             work_description_store=persistence_store))])

    # Ensure Client authentication
    ssl_ctx = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    ssl_ctx.load_cert_chain(local_certs_file, key_file)
    # The docs suggest we have to specify both that we must verify the client cert and the locations
    ssl_ctx.verify_mode = ssl.CERT_REQUIRED
    ssl_ctx.load_verify_locations(ca_certs_file)

    inbound_server = tornado.httpserver.HTTPServer(inbound_application, ssl_options=ssl_ctx)
    inbound_server.listen(443)

    healthcheck_application = tornado.web.Application([
        ("/healthcheck", healthcheck_handler.HealthcheckHandler)
    ])
    healthcheck_application.listen(80)

    logger.info('011', 'Starting inbound server')
    tornado.ioloop.IOLoop.current().start()


def main():
    config.setup_config("MHS")
    secrets.setup_secret_config("MHS")
    log.configure_logging()

    certificates = certs.Certs.create_certs_files(definitions.ROOT_DIR,
                                                  private_key=secrets.get_secret_config('CLIENT_KEY'),
                                                  local_cert=secrets.get_secret_config('CLIENT_CERT'),
                                                  ca_certs=secrets.get_secret_config('CA_CERTS'))
    party_key = secrets.get_secret_config('PARTY_KEY')

    workflows = initialise_workflows()
    store = dynamo_persistence_adaptor.DynamoPersistenceAdaptor(table_name=config.get_config('STATE_TABLE_NAME'))

    start_inbound_server(certificates.local_cert_path, certificates.ca_certs_path, certificates.private_key_path,
                         party_key, workflows, store)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.critical('001', 'Fatal exception in main application: {exception}', {'exception': e})
    finally:
        logger.info('002', 'Exiting application')
