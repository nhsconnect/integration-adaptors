import ssl
import ldap3


def build_sds_connection(ldap_address: str) -> ldap3.Connection:
    """
    Given an ip address this will return a ldap3 connection object
    """
    server = ldap3.Server(ldap_address)
    connection = ldap3.Connection(server, auto_bind=True, client_strategy=ldap3.REUSABLE)
    return connection


def build_sds_connection_tls(ldap_address: str,
                             private_key_path: str,
                             local_cert_path: str,
                             ca_certs_file: str
                             ) -> ldap3.Connection:
    """
    This will return a connection object for the given ip along with loading the given certification files
    :return: Connection object using the given cert files
    """

    load_tls = ldap3.Tls(local_private_key_file=private_key_path,
                         local_certificate_file=local_cert_path,
                         validate=ssl.CERT_REQUIRED, version=ssl.PROTOCOL_TLSv1,
                         ca_certs_file=ca_certs_file)

    server = ldap3.Server(ldap_address, use_ssl=True, tls=load_tls)
    connection = ldap3.Connection(server, auto_bind=True, client_strategy=ldap3.REUSABLE)
    return connection
