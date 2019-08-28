import pathlib

import tornado.httpserver
import tornado.ioloop
import tornado.web
from utilities import config
from utilities import integration_adaptors_logger as log

import definitions
from lookup import dictionary_cache, sds_connection_factory, sds_client, mhs_attribute_lookup, routing_reliability
from request import routing_handler, reliability_handler, routing_reliability_handler

logger = log.IntegrationAdaptorsLogger('SPINE_ROUTE_LOOKUP_MAIN')


def initialise_routing(sds_url: str, tls: bool = True) -> routing_reliability.RoutingAndReliability:
    """Initialise the routing and reliability component to be used for SDS queries.

    :param sds_url: The URL to communicate with SDS on.
    :param tls: A flag to indicate whether TLS should be enabled for the SDS connection.
    :return:
    """
    logger.info('004', 'Configuring connection to SDS using {url} {tls}', {"url": sds_url, "tls": tls})

    cache = dictionary_cache.DictionaryCache()

    if tls:
        certs_dir = pathlib.Path(definitions.ROOT_DIR) / "data" / "certs"
        private_key_path = str(certs_dir / "client.key")
        cert_path = str(certs_dir / "client.pem")
        ca_certs_path = str(certs_dir / "ca_certs.pem")
        sds_connection = sds_connection_factory.build_sds_connection_tls(ldap_address=sds_url,
                                                                         private_key_path=private_key_path,
                                                                         local_cert_path=cert_path,
                                                                         ca_certs_file=ca_certs_path)
    else:
        sds_connection = sds_connection_factory.build_sds_connection(ldap_address=sds_url)

    client = sds_client.SDSClient(sds_connection)
    attribute_lookup = mhs_attribute_lookup.MHSAttributeLookup(client=client, cache=cache)
    routing = routing_reliability.RoutingAndReliability(attribute_lookup)
    return routing


def start_tornado_server(routing: routing_reliability.RoutingAndReliability) -> None:
    """Start the Tornado server

    :param routing: The routing/reliability component to be used when servicing requests.
    """
    handler_dependencies = {"routing": routing}
    application = tornado.web.Application([
        ("/routing", routing_handler.RoutingRequestHandler, handler_dependencies),
        ("/reliability", reliability_handler.ReliabilityRequestHandler, handler_dependencies),
        ("/routing-reliability", routing_reliability_handler.RoutingReliabilityRequestHandler, handler_dependencies)
    ])
    server = tornado.httpserver.HTTPServer(application)
    server.listen(80)

    logger.info('003', 'Starting server')
    tornado.ioloop.IOLoop.current().start()


def main():
    config.setup_config("MHS")
    log.configure_logging()

    sds_url = config.get_config("SDS_URL")
    disable_tls_flag = config.get_config("DISABLE_SDS_TLS", None)
    use_tls = disable_tls_flag != "True"

    routing = initialise_routing(sds_url=sds_url, tls=use_tls)
    start_tornado_server(routing)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.critical('001', 'Fatal exception in main application: {exception}', {'exception': e})
    finally:
        logger.info('002', 'Exiting application')
