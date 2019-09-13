import pathlib
import ssl
from typing import Tuple

import ldap3

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
    private_key_file, local_cert_file, ca_certs_file = _create_certs(private_key, local_cert, ca_certs)

    load_tls = ldap3.Tls(local_private_key_file=private_key_file, local_certificate_file=local_cert_file,
                         validate=ssl.CERT_REQUIRED, version=ssl.PROTOCOL_TLSv1, ca_certs_file=ca_certs_file)

    server = ldap3.Server(ldap_address, use_ssl=True, tls=load_tls)
    connection = ldap3.Connection(server, auto_bind=True, client_strategy=ldap3.REUSABLE)
    return connection


def _create_certs(private_key: str, local_cert: str, ca_certs: str) -> Tuple[str, str, str]:
    certs_dir = pathlib.Path(definitions.ROOT_DIR) / "data" / "certs"
    private_key_file = (certs_dir / "client.key")
    local_cert_file = (certs_dir / "client.pem")
    ca_certs_file = (certs_dir / "ca_certs.pem")

    certs_dir.mkdir(parents=True, exist_ok=True)
    private_key_file.write_text(private_key)
    local_cert_file.write_text(local_cert)
    ca_certs_file.write_text(ca_certs)

    return str(private_key_file), str(local_cert_file), str(ca_certs_file)
