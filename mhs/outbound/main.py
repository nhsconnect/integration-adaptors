import pathlib
from typing import Tuple

import tornado.httpserver
import tornado.ioloop
import tornado.web

import definitions
import configuration.configuration_manager as configuration_manager
import workflow.sync_async as sync_async_workflow

import request.synchronous.handler as client_request_handler
import transmission.outbound_transmission as outbound_transmission
import utilities.config as config
import utilities.file_utilities as file_utilities
import utilities.integration_adaptors_logger as log

logger = log.IntegrationAdaptorsLogger('OUTBOUND_MAIN')

ASYNC_TIMEOUT = 30


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


def initialise_workflow(data_dir: pathlib.Path, certs_dir: pathlib.Path,
                        party_key: str) -> sync_async_workflow.SyncAsyncWorkflow:
    """Initialise the
    :param data_dir: The directory to load interactions configuration from.
    :param certs_dir: The directory containing certificates/keys to be used to identify this MHS to a remote MHS.
    :param party_key: The party key to use to identify this MHS.
    :return: The workflow that can be used to handle messages.
    """
    interactions_config_file = str(data_dir / "interactions" / "interactions.json")
    config_manager = configuration_manager.ConfigurationManager(interactions_config_file)

    transmission = outbound_transmission.OutboundTransmission(str(certs_dir))

    workflow = sync_async_workflow.SyncAsyncWorkflow(config_manager, transmission, party_key)

    return workflow


def start_tornado_server(workflow: sync_async_workflow.SyncAsyncWorkflow) -> None:
    """
    :param certs_file: The filename of the certificate to be used to identify this MHS to a remote MHS.
    :param key_file: The filename of the private key for the certificate identified by certs_file.
    :param workflow: The workflow to be used to handle messages.
    :param party_key: The party key to use to identify this MHS.
    """
    callbacks = {}

    supplier_application = tornado.web.Application(
        [(r"/(.*)", client_request_handler.SynchronousHandler,
          dict(workflow=workflow, callbacks=callbacks, async_timeout=ASYNC_TIMEOUT))])
    supplier_server = tornado.httpserver.HTTPServer(supplier_application)
    supplier_server.listen(80)

    logger.info('011', 'Starting outbound server')
    tornado.ioloop.IOLoop.current().start()


def main():
    config.setup_config("MHS")
    log.configure_logging()
    data_dir = pathlib.Path(definitions.ROOT_DIR) / "data"
    certs_dir = data_dir / "certs"
    party_key = load_party_key(certs_dir)
    workflow = initialise_workflow(data_dir, certs_dir, party_key)
    start_tornado_server(workflow)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.critical('001', 'Fatal exception in main application: {exception}', {'exception': e})
    finally:
        logger.info('002', 'Exiting application')