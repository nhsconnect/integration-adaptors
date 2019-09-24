from __future__ import annotations

import pathlib
from typing import Union


class Certs(object):
    """A collection of certificates and keys.

    Attributes:
        - private_key_path: A string containing the full path to client certificate private key.
        - local_cert_path: A string containing the full path to client certificate.
        - ca_certs_path: A string containing the full path to the CA certificates.
    """

    def __init__(self):
        """Create an empty Certs object."""
        self.private_key_path = None
        self.local_cert_path = None
        self.ca_certs_path = None

    @staticmethod
    def create_certs_files(root_dir: Union[str, pathlib.Path], *,
                           private_key: str = None, local_cert: str = None, ca_certs: str = None) -> Certs:
        """
        Create files that hold certificate data in a root_dir/data/certs folder (creating missing folders as
        appropriate).

        :param root_dir: root dir in which to create data/certs folders in which to store the cert data
        :param private_key: private key to store in client.key file
        :param local_cert: local cert to store in client.pem file
        :param ca_certs: CA certs to store in ca_certs.pem file
        :return: A Certs object containing details of the certificates created.
        """
        certs_dir = pathlib.Path(root_dir) / "data" / "certs"
        certs_dir.mkdir(parents=True, exist_ok=True)

        created_certs = Certs()
        if private_key:
            private_key_file = certs_dir / "client.key"
            private_key_file.write_text(private_key)
            created_certs.private_key_path = str(private_key_file)

        if local_cert:
            local_cert_file = certs_dir / "client.pem"
            local_cert_file.write_text(local_cert)
            created_certs.local_cert_path = str(local_cert_file)

        if ca_certs:
            ca_certs_file = certs_dir / "ca_certs.pem"
            ca_certs_file.write_text(ca_certs)
            created_certs.ca_certs_path = str(ca_certs_file)

        return created_certs
