import pathlib
from typing import Dict

import definitions
import mhs_common.configuration.configuration_manager as configuration_manager
import tornado.httpclient
import tornado.httpserver
import tornado.ioloop
import tornado.web
from mhs_common import workflow
from mhs_common.request import healthcheck_handler
from mhs_common.state import dynamo_persistence_adaptor, persistence_adaptor
import outbound.request.synchronous.handler as client_request_handler
import utilities.config as config
import utilities.integration_adaptors_logger as log
from outbound.transmission import outbound_transmission
from mhs_common.workflow import sync_async_resynchroniser as resync

logger = log.IntegrationAdaptorsLogger('OUTBOUND_MAIN')


def configure_http_client():
    """
    Configure Tornado to use the curl HTTP client.
    """
    tornado.httpclient.AsyncHTTPClient.configure('tornado.curl_httpclient.CurlAsyncHTTPClient')


def initialise_workflows(transmission: outbound_transmission.OutboundTransmission, party_key: str,
                         work_description_store: persistence_adaptor.PersistenceAdaptor,
                         sync_async_store: persistence_adaptor.PersistenceAdaptor,
                         persistence_store_retries: int) \
        -> Dict[str, workflow.CommonWorkflow]:
    """Initialise the workflows
    :param sync_async_store:
    :param transmission: The transmission object to be used to make requests to the spine endpoints
    :param party_key: The party key to use to identify this MHS.
    :param work_description_store: The persistence adaptor for the state database
    :return: The workflows that can be used to handle messages.
    """

    resynchroniser = resync.SyncAsyncResynchroniser(sync_async_store,
                                                    int(config.get_config('RESYNC_RETRIES', '20')),
                                                    float(config.get_config('RESYNC_INTERVAL', '1.0')))

    return workflow.get_workflow_map(party_key,
                                     work_description_store=work_description_store,
                                     transmission=transmission,
                                     resynchroniser=resynchroniser,
                                     persistence_store_max_retries=persistence_store_retries
                                     )


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
          dict(config_manager=config_manager, workflows=workflows)),
         (r"/healthcheck", healthcheck_handler.HealthcheckHandler)])
    supplier_server = tornado.httpserver.HTTPServer(supplier_application)
    supplier_server.listen(80)

    logger.info('001', 'Starting servers')
    tornado.ioloop.IOLoop.current().start()


def main():
    config.setup_config("MHS")
    log.configure_logging()

    configure_http_client()

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
    store_retries = int(config.get_config('STATE_STORE_MAX_RETRIES', default='3'))

    party_key = config.get_config('PARTY_KEY')
    work_description_store = dynamo_persistence_adaptor.DynamoPersistenceAdaptor(
        table_name=config.get_config('STATE_TABLE_NAME'))
    sync_async_store = dynamo_persistence_adaptor.DynamoPersistenceAdaptor(
        table_name=config.get_config('SYNC_ASYNC_STATE_TABLE_NAME'))

    http_proxy_host = config.get_config('OUTBOUND_HTTP_PROXY', default=None)
    http_proxy_port = None
    if http_proxy_host is not None:
        http_proxy_port = int(config.get_config('OUTBOUND_HTTP_PROXY_PORT', default="3128"))
    transmission = outbound_transmission.OutboundTransmission(str(certs_dir), client_cert, client_key, ca_certs,
                                                              max_retries, retry_delay, http_proxy_host,
                                                              http_proxy_port)

    workflows = initialise_workflows(transmission, party_key, work_description_store, sync_async_store, store_retries)
    start_tornado_server(data_dir, workflows)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.critical('002', 'Fatal exception in main application: {exception}', {'exception': e})
    finally:
        logger.info('003', 'Exiting application')
