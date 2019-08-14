import pathlib
from typing import Dict

import tornado.httpserver
import tornado.ioloop
import tornado.web

import definitions
import mhs_common.configuration.configuration_manager as configuration_manager
from mhs_common.state import dynamo_persistence_adaptor, persistence_adaptor

import outbound.request.synchronous.handler as client_request_handler
import utilities.config as config
import utilities.file_utilities as file_utilities
import utilities.integration_adaptors_logger as log
from mhs_common import workflow

logger = log.IntegrationAdaptorsLogger('OUTBOUND_MAIN')


def load_party_key(data_dir: pathlib.Path) -> str:
    """Load this MHS's party key from the specified directory.
    :param data_dir: The directory to load the party key from.
    :return: The party key to use to identify this MHS.
    """
    party_key_file = str(data_dir / "party_key.txt")
    party_key = file_utilities.FileUtilities.get_file_string(party_key_file)

    assert party_key
    return party_key


def initialise_workflows(certs_dir: pathlib.Path, party_key: str,
                         persistence_store: persistence_adaptor.PersistenceAdaptor) \
        -> Dict[str, workflow.CommonWorkflow]:
    """Initialise the workflows
    :param certs_dir: The directory containing certificates/keys to be used to identify this MHS to a remote MHS.
    :param party_key: The party key to use to identify this MHS.
    :param persistence_store: The persistence adaptor for the state database
    :return: The workflows that can be used to handle messages.
    """
    # transmission = outbound_transmission.OutboundTransmission(str(certs_dir))
    # workflow = sync_async_workflow.SyncAsyncWorkflow(transmission, party_key)

    return workflow.get_workflow_map(persistence_store)


def start_tornado_server(data_dir: pathlib.Path, workflows: Dict[str, workflow.CommonWorkflow]) -> None:
    """
    Start Tornado server
    :param data_dir: The directory to load interactions configuration from.
    :param workflows: The workflows to be used to handle messages.
    """
    interactions_config_file = str(data_dir / "interactions" / "interactions.json")
    config_manager = configuration_manager.ConfigurationManager(interactions_config_file)

    supplier_application = tornado.web.Application(
        [(r"/", client_request_handler.SynchronousHandler,
          dict(config_manager=config_manager, workflows=workflows))])
    supplier_server = tornado.httpserver.HTTPServer(supplier_application)
    supplier_server.listen(80)

    logger.info('001', 'Starting servers')
    tornado.ioloop.IOLoop.current().start()


def main():
    config.setup_config("MHS")
    log.configure_logging()

    data_dir = pathlib.Path(definitions.ROOT_DIR) / "data"
    certs_dir = data_dir / "certs"
    party_key = load_party_key(certs_dir)
    persistence_store = dynamo_persistence_adaptor.DynamoPersistenceAdaptor(
        table_name=config.get_config('STATE_TABLE_NAME'))

    workflows = initialise_workflows(certs_dir, party_key, persistence_store)

    start_tornado_server(data_dir, workflows)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.critical('002', 'Fatal exception in main application: {exception}', {'exception': e})
    finally:
        logger.info('003', 'Exiting application')
