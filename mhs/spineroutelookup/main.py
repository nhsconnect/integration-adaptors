import tornado.httpserver
import tornado.ioloop
import tornado.web
from mhs_common.request import healthcheck_handler
from utilities import config, secrets
from utilities import integration_adaptors_logger as log

from lookup import cache_adaptor, redis_cache, sds_connection_factory, sds_client, mhs_attribute_lookup, \
    routing_reliability
from request import routing_handler, reliability_handler, routing_reliability_handler

logger = log.IntegrationAdaptorsLogger('SPINE_ROUTE_LOOKUP_MAIN')


def load_cache_implementation():
    cache_expiry_time = int(config.get_config("SDS_CACHE_EXPIRY_TIME", cache_adaptor.FIFTEEN_MINUTES_IN_SECONDS))

    redis_host = config.get_config("SDS_REDIS_CACHE_HOST")
    redis_port = int(config.get_config("SDS_REDIS_CACHE_PORT", "6379"))
    disable_tls_flag = config.get_config("SDS_REDIS_DISABLE_TLS", None)
    use_tls = disable_tls_flag != "True"

    logger.info('005', 'Using the Redis cache with {redis_host}, {redis_port}, {cache_expiry_time}, {use_tls}',
                {'redis_host': redis_host, 'redis_port': redis_port, 'cache_expiry_time': cache_expiry_time,
                 'use_tls': use_tls})
    return redis_cache.RedisCache(redis_host, redis_port, cache_expiry_time, use_tls)


def initialise_routing(sds_url: str, search_base: str, tls: bool = True) -> routing_reliability.RoutingAndReliability:
    """Initialise the routing and reliability component to be used for SDS queries.

    :param sds_url: The URL to communicate with SDS on.
    :param search_base: The LDAP location to use as the base of SDS searched. e.g. ou=services,o=nhs.
    :param tls: A flag to indicate whether TLS should be enabled for the SDS connection.
    :return:
    """
    logger.info('004', 'Configuring connection to SDS using {url} {tls}', {"url": sds_url, "tls": tls})

    cache = load_cache_implementation()

    if tls:
        client_key = secrets.get_secret_config('CLIENT_KEY')
        client_cert = secrets.get_secret_config('CLIENT_CERT')
        ca_certs = secrets.get_secret_config('CA_CERTS')
        logger.info('004', 'Creating sds connection - TLS')
        sds_connection = sds_connection_factory.build_sds_connection_tls(ldap_address=sds_url,
                                                                         private_key=client_key,
                                                                         local_cert=client_cert,
                                                                         ca_certs=ca_certs)
    else:
        logger.info('004', 'Creating sds connection - non TLS')
        sds_connection = sds_connection_factory.build_sds_connection(ldap_address=sds_url)

    logger.info('004', 'Creating SDS client')
    client = sds_client.SDSClient(sds_connection, search_base)
    logger.info('004', 'Creating MHS attribute lookup')
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
        ("/routing-reliability", routing_reliability_handler.RoutingReliabilityRequestHandler, handler_dependencies),
        ("/healthcheck", healthcheck_handler.HealthcheckHandler)
    ])
    server = tornado.httpserver.HTTPServer(application)
    server.listen(80)

    logger.info('003', 'Starting server')
    tornado.ioloop.IOLoop.current().start()


def main():
    config.setup_config("MHS")
    secrets.setup_secret_config("MHS")
    log.configure_logging()

    sds_url = config.get_config("SDS_URL")
    disable_tls_flag = config.get_config("DISABLE_SDS_TLS", None)
    use_tls = disable_tls_flag != "True"
    search_base = config.get_config("SDS_SEARCH_BASE")

    routing = initialise_routing(sds_url=sds_url, search_base=search_base, tls=use_tls)
    start_tornado_server(routing)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.critical('001', 'Fatal exception in main application: {exception}', {'exception': e})
    finally:
        logger.info('002', 'Exiting application')
