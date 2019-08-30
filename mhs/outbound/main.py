import pathlib
from typing import Dict

import definitions
import mhs_common.configuration.configuration_manager as configuration_manager
import tornado.httpserver
import tornado.ioloop
import tornado.web
import utilities.config as config
import utilities.file_utilities as file_utilities
import utilities.integration_adaptors_logger as log
from mhs_common import workflow
from mhs_common.state import dynamo_persistence_adaptor, persistence_adaptor

import outbound.request.synchronous.handler as client_request_handler
from outbound.transmission import outbound_transmission

logger = log.IntegrationAdaptorsLogger('OUTBOUND_MAIN')


def initialise_workflows(transmission: outbound_transmission.OutboundTransmission, party_key: str,
                         persistence_store: persistence_adaptor.PersistenceAdaptor) \
        -> Dict[str, workflow.CommonWorkflow]:
    """Initialise the workflows
    :param transmission: The transmission object to be used to make requests to the spine endpoints
    :param party_key: The party key to use to identify this MHS.
    :param persistence_store: The persistence adaptor for the state database
    :return: The workflows that can be used to handle messages.
    """

    return workflow.get_workflow_map(party_key,work_description_store=persistence_store, transmission=transmission)


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
    client_cert = "client.cert"
    client_key = "client.key"
    ca_certs = "client.pem"

    certs_dir.mkdir(parents=True, exist_ok=True)
    (certs_dir / client_cert).write_text(config.get_config('CLIENT_CERT'))
    (certs_dir / client_key).write_text(config.get_config('CLIENT_KEY'))
    (certs_dir / ca_certs).write_text(config.get_config('CA_CERTS'))

    max_retries = int(config.get_config('OUTBOUND_TRANSMISSION_MAX_RETRIES', default="3"))
    retry_delay = int(config.get_config('OUTBOUND_TRANSMISSION_RETRY_DELAY', default="100"))
    party_key = config.get_config('PARTY_KEY')
    persistence_store = dynamo_persistence_adaptor.DynamoPersistenceAdaptor(
        table_name=config.get_config('STATE_TABLE_NAME'))

    transmission = outbound_transmission.OutboundTransmission(str(certs_dir), client_cert, client_key, ca_certs,
                                                              max_retries, retry_delay)
    workflows = initialise_workflows(transmission, party_key, persistence_store)

    start_tornado_server(data_dir, workflows)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.critical('002', 'Fatal exception in main application: {exception}', {'exception': e})
    finally:
        logger.info('003', 'Exiting application')
