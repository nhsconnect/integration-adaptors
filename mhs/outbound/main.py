import pathlib
from typing import Dict

import definitions
import mhs_common.configuration.configuration_manager as configuration_manager
import tornado.httpclient
import tornado.httpserver
import tornado.ioloop
import tornado.web
import utilities.integration_adaptors_logger as log
from mhs_common import workflow
from mhs_common.request import healthcheck_handler
from mhs_common.routing import routing_reliability
from mhs_common.state import dynamo_persistence_adaptor, persistence_adaptor
from mhs_common.workflow import sync_async_resynchroniser as resync
from utilities import config, certs
from utilities import secrets

import outbound.request.synchronous.handler as client_request_handler
from outbound.transmission import outbound_transmission

logger = log.IntegrationAdaptorsLogger('OUTBOUND_MAIN')


def configure_http_client():
    """
    Configure Tornado to use the curl HTTP client.
    """
    tornado.httpclient.AsyncHTTPClient.configure('tornado.curl_httpclient.CurlAsyncHTTPClient')


def initialise_workflows(transmission: outbound_transmission.OutboundTransmission, party_key: str,
                         work_description_store: persistence_adaptor.PersistenceAdaptor,
                         sync_async_store: persistence_adaptor.PersistenceAdaptor,
                         max_request_size: int,
                         persistence_store_retries: int,
                         routing: routing_reliability.RoutingAndReliability) \
        -> Dict[str, workflow.CommonWorkflow]:
    """Initialise the workflows
    :param transmission: The transmission object to be used to make requests to the spine endpoints
    :param party_key: The party key to use to identify this MHS.
    :param work_description_store: The persistence adaptor for the state database.
    :param sync_async_store: The persistence adaptor for the sync-async database.
    :param max_request_size: The maximum size of the request body that gets sent to Spine.
    :param persistence_store_retries The number of times to retry storing values in the work description or sync-async
    databases.
    :param routing: The routing and reliability component to use to request routing/reliability details
    from.
    :return: The workflows that can be used to handle messages.
    """

    resynchroniser = resync.SyncAsyncResynchroniser(sync_async_store,
                                                    int(config.get_config('RESYNC_RETRIES', '20')),
                                                    float(config.get_config('RESYNC_INTERVAL', '1.0')),
                                                    float(config.get_config('RESYNC_INITIAL_DELAY', '0')))

    return workflow.get_workflow_map(party_key,
                                     work_description_store=work_description_store,
                                     transmission=transmission,
                                     resynchroniser=resynchroniser,
                                     max_request_size=max_request_size,
                                     persistence_store_max_retries=persistence_store_retries,
                                     routing=routing
                                     )


def initialise_routing():
    spine_route_lookup_url = config.get_config('SPINE_ROUTE_LOOKUP_URL')
    spine_org_code = config.get_config('SPINE_ORG_CODE')

    route_data_dir = pathlib.Path(definitions.ROOT_DIR) / "route"
    certificates = certs.Certs.create_certs_files(route_data_dir,
                                                  private_key=secrets.get_secret_config('SPINE_ROUTE_LOOKUP_CLIENT_KEY',
                                                                                        default=None),
                                                  local_cert=secrets.get_secret_config('SPINE_ROUTE_LOOKUP_CLIENT_CERT',
                                                                                       default=None),
                                                  ca_certs=secrets.get_secret_config('SPINE_ROUTE_LOOKUP_CA_CERTS',
                                                                                     default=None))

    route_proxy_host = config.get_config('SPINE_ROUTE_LOOKUP_HTTP_PROXY', default=None)
    route_proxy_port = None
    if route_proxy_host is not None:
        route_proxy_port = int(config.get_config('SPINE_ROUTE_LOOKUP_HTTP_PROXY_PORT', default="3128"))

    return routing_reliability.RoutingAndReliability(spine_route_lookup_url, spine_org_code,
                                                     client_cert=certificates.local_cert_path,
                                                     client_key=certificates.private_key_path,
                                                     ca_certs=certificates.ca_certs_path,
                                                     http_proxy_host=route_proxy_host, http_proxy_port=route_proxy_port)


def start_tornado_server(data_dir: pathlib.Path, workflows: Dict[str, workflow.CommonWorkflow]) -> None:
    """
    Start Tornado server
    :param data_dir: The directory to load interactions configuration from.
    :param workflows: The workflows to be used to handle messages.
    """
    interactions_config_file = str(data_dir / "interactions" / "interactions.json")
    config_manager = configuration_manager.ConfigurationManager(interactions_config_file)

    # Note that the paths in generate_openapi.py should be updated if these
    # paths are changed
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
    secrets.setup_secret_config("MHS")
    log.configure_logging()
    data_dir = pathlib.Path(definitions.ROOT_DIR) / "data"

    configure_http_client()

    routing = initialise_routing()

    certificates = certs.Certs.create_certs_files(data_dir / '..',
                                                  private_key=secrets.get_secret_config('CLIENT_KEY'),
                                                  local_cert=secrets.get_secret_config('CLIENT_CERT'),
                                                  ca_certs=secrets.get_secret_config('CA_CERTS'))
    max_retries = int(config.get_config('OUTBOUND_TRANSMISSION_MAX_RETRIES', default="3"))
    retry_delay = int(config.get_config('OUTBOUND_TRANSMISSION_RETRY_DELAY', default="100"))
    http_proxy_host = config.get_config('OUTBOUND_HTTP_PROXY', default=None)
    http_proxy_port = None
    if http_proxy_host is not None:
        http_proxy_port = int(config.get_config('OUTBOUND_HTTP_PROXY_PORT', default="3128"))
    transmission = outbound_transmission.OutboundTransmission(certificates.local_cert_path,
                                                              certificates.private_key_path, certificates.ca_certs_path,
                                                              max_retries, retry_delay, http_proxy_host,
                                                              http_proxy_port)

    party_key = secrets.get_secret_config('PARTY_KEY')
    work_description_store = dynamo_persistence_adaptor.DynamoPersistenceAdaptor(
        table_name=config.get_config('STATE_TABLE_NAME'))
    sync_async_store = dynamo_persistence_adaptor.DynamoPersistenceAdaptor(
        table_name=config.get_config('SYNC_ASYNC_STATE_TABLE_NAME'))
    store_retries = int(config.get_config('STATE_STORE_MAX_RETRIES', default='3'))
    max_request_size = int(config.get_config('SPINE_REQUEST_MAX_SIZE'))
    workflows = initialise_workflows(transmission, party_key, work_description_store, sync_async_store,
                                     max_request_size, store_retries, routing)
    start_tornado_server(data_dir, workflows)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.critical('002', 'Fatal exception in main application: {exception}', {'exception': e})
    finally:
        logger.info('003', 'Exiting application')
