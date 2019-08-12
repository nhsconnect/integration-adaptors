import pathlib
import ssl
from typing import Tuple, Dict

import tornado.httpserver
import tornado.ioloop
import tornado.web

import definitions
import mhs.common.configuration.configuration_manager as configuration_manager
import mhs.inbound.request.handler as async_request_handler
import mhs.outbound.request.synchronous.handler as client_request_handler
import utilities.config as config
import utilities.file_utilities as file_utilities
import utilities.integration_adaptors_logger as log
from mhs.common import workflow

logger = log.IntegrationAdaptorsLogger('MHS_MAIN')


def load_certs(certs_dir: pathlib.Path) -> Tuple[str, str]:
    """Load the necessary TLS certificates from the specified directory.

    :param certs_dir: The directory to load certificates from.
    :return: A tuple consisting of the file names of the client's certificates file, and the client's key.
    """
    certs_file = str(certs_dir / "client.pem")
    key_file = str(certs_dir / "client.key")

    return certs_file, key_file


def load_party_key(data_dir: pathlib.Path) -> str:
    """Load this MHS's party key from the specified directory.

    :param data_dir: The directory to load the party key from.
    :return: The party key to use to identify this MHS.
    """
    party_key_file = str(data_dir / "party_key.txt")
    party_key = file_utilities.FileUtilities.get_file_string(party_key_file)

    assert party_key
    return party_key


def initialise_workflows(certs_dir: pathlib.Path, party_key: str) -> Dict[str, workflow.CommonWorkflow]:
    """Initialise the workflows

    :param certs_dir: The directory containing certificates/keys to be used to identify this MHS to a remote MHS.
    :param party_key: The party key to use to identify this MHS.
    :return: The workflows that can be used to handle messages.
    """
    # transmission = outbound_transmission.OutboundTransmission(str(certs_dir))
    # workflow = sync_async_workflow.SyncAsyncWorkflow(transmission, party_key)

    return workflow.get_workflow_map()


def start_tornado_servers(data_dir: pathlib.Path, certs_file: str, key_file: str,
                          workflows: Dict[str, workflow.CommonWorkflow], party_key: str) -> None:
    """

    :param data_dir: The directory to load interactions configuration from.
    :param certs_file: The filename of the certificate to be used to identify this MHS to a remote MHS.
    :param key_file: The filename of the private key for the certificate identified by certs_file.
    :param workflows: The workflows to be used to handle messages.
    :param party_key: The party key to use to identify this MHS.
    """
    callbacks = {}

    interactions_config_file = str(data_dir / "interactions" / "interactions.json")
    config_manager = configuration_manager.ConfigurationManager(interactions_config_file)

    supplier_application = tornado.web.Application(
        [(r"/", client_request_handler.SynchronousHandler,
          dict(config_manager=config_manager, workflows=workflows))])
    supplier_server = tornado.httpserver.HTTPServer(supplier_application)
    supplier_server.listen(80)

    mhs_application = tornado.web.Application(
        [(r"/.*", async_request_handler.InboundHandler, dict(callbacks=callbacks, party_id=party_key))])
    mhs_server = tornado.httpserver.HTTPServer(mhs_application,
                                               ssl_options=dict(certfile=certs_file, keyfile=key_file,
                                                                cert_reqs=ssl.CERT_REQUIRED,
                                                                ca_certs=certs_file))
    mhs_server.listen(443)

    logger.info('001', 'Starting servers')
    tornado.ioloop.IOLoop.current().start()


def main():
    config.setup_config("MHS")
    log.configure_logging()

    data_dir = pathlib.Path(definitions.ROOT_DIR) / "data"
    certs_dir = data_dir / "certs"
    certs_file, key_file = load_certs(certs_dir)
    party_key = load_party_key(certs_dir)

    workflows = initialise_workflows(certs_dir, party_key)

    start_tornado_servers(data_dir, certs_file, key_file, workflows, party_key)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.critical('002', 'Fatal exception in main application: {exception}', {'exception': e})
    finally:
        logger.info('003', 'Exiting application')
