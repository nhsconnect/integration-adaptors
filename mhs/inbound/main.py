import pathlib
import ssl
from typing import Tuple, Dict

import definitions
import tornado.httpserver
import tornado.ioloop
import tornado.web
import utilities.config as config
import utilities.file_utilities as file_utilities
import utilities.integration_adaptors_logger as log
from comms import proton_queue_adaptor
from mhs_common import workflow
from mhs_common.request import healthcheck_handler
from mhs_common.state import persistence_adaptor, dynamo_persistence_adaptor
from utilities import secrets

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


def load_certs(certs_dir: pathlib.Path) -> Tuple[str, str]:
    """Load the necessary TLS certificates from config into the specified directory.

    :param certs_dir: The directory to load certificates from.
    :return: A tuple consisting of the file names of the client's certificates file, and the client's key.
    """

    certs_file = certs_dir / "client.pem"
    key_file = certs_dir / "client.key"

    certs_dir.mkdir(parents=True, exist_ok=True)
    certs_file.write_text(secrets.get_secret_config('CA_CERTS'))
    key_file.write_text(secrets.get_secret_config('CLIENT_KEY'))

    return str(certs_file), str(key_file)


def load_party_key(data_dir: pathlib.Path) -> str:
    """Load this MHS's party key from the specified directory.

    :param data_dir: The directory to load the party key from.
    :return: The party key to use to identify this MHS.
    """
    party_key_file = str(data_dir / "party_key.txt")
    party_key = file_utilities.FileUtilities.get_file_string(party_key_file)

    assert party_key
    return party_key


def start_inbound_server(certs_file: str, key_file: str, party_key: str,
                         workflows: Dict[str, workflow.CommonWorkflow],
                         persistence_store: persistence_adaptor.PersistenceAdaptor
                         ) -> None:
    """

    :param persistence_store: persistence store adaptor for message information
    :param certs_file: The filename of the certificate to be used to identify this MHS to a remote MHS.
    :param key_file: The filename of the private key for the certificate identified by certs_file.
    :param workflows: The workflows to be used to handle messages.
    :param party_key: The party key to use to identify this MHS.
    """

    inbound_application = tornado.web.Application(
        [(r"/.*", async_request_handler.InboundHandler, dict(workflows=workflows, party_id=party_key,
                                                             work_description_store=persistence_store))])

    # Ensure Client authentication
    ssl_ctx = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    ssl_ctx.load_cert_chain(certs_file, key_file)
    # The docs suggest we have to specify both that we must verify the client cert and the locations
    ssl_ctx.verify_mode = ssl.CERT_REQUIRED
    ssl_ctx.load_verify_locations(certs_file)

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
    log.configure_logging()

    data_dir = pathlib.Path(definitions.ROOT_DIR) / "data"
    certs_dir = data_dir / "certs"
    certs_file, key_file = load_certs(certs_dir)
    party_key = secrets.get_secret_config('PARTY_KEY')

    workflows = initialise_workflows()
    store = dynamo_persistence_adaptor.DynamoPersistenceAdaptor(table_name=config.get_config('STATE_TABLE_NAME'))

    start_inbound_server(certs_file, key_file, party_key, workflows, store)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.critical('001', 'Fatal exception in main application: {exception}', {'exception': e})
    finally:
        logger.info('002', 'Exiting application')
