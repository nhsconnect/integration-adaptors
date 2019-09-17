import ssl

import ldap3
from mhs_common import certs

import definitions


def build_sds_connection(ldap_address: str) -> ldap3.Connection:
    """
    Given an ldap service address this will return a ldap3 connection object
    """
    server = ldap3.Server(ldap_address)
    connection = ldap3.Connection(server, auto_bind=True, client_strategy=ldap3.REUSABLE)
    return connection


def build_sds_connection_tls(ldap_address: str, private_key: str, local_cert: str, ca_certs: str
                             ) -> ldap3.Connection:
    """
    This will return a connection object for the given ip along with loading the given certification files
    :param ldap_address: The URL of the LDAP server to connect to.
    :param private_key: A string containing the client private key.
    :param local_cert: A string containing the client certificate.
    :param ca_certs: A string containing certificate authority certificates
    :return: Connection object using the given cert files
    """
    private_key_file, local_cert_file, ca_certs_file = certs.create_certs_files(definitions.ROOT_DIR,
                                                                                private_key=private_key,
                                                                                local_cert=local_cert,
                                                                                ca_certs=ca_certs)

    load_tls = ldap3.Tls(local_private_key_file=private_key_file, local_certificate_file=local_cert_file,
                         validate=ssl.CERT_REQUIRED, version=ssl.PROTOCOL_TLSv1, ca_certs_file=ca_certs_file)

    server = ldap3.Server(ldap_address, use_ssl=True, tls=load_tls)
    return ldap3.Connection(server, auto_bind=True, client_strategy=ldap3.REUSABLE)
