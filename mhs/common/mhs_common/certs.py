import pathlib
from typing import Tuple, Union


def create_certs_files(root_dir: Union[str, pathlib.Path], *,
                       private_key: str = None, local_cert: str = None, ca_certs: str = None) -> Tuple[str, ...]:
    """
    Create files that hold certificate data in a root_dir/data/certs folder (creating missing folders as appropriate).

    :param root_dir: root dir in which to create data/certs folders in which to store the cert data
    :param private_key: private key to store in client.key file
    :param local_cert: local cert to store in client.pem file
    :param ca_certs: CA certs to store in ca_certs.pem file
    :return: a tuple of strings of the filepaths of the created files, in the order
    (private_key_file, local_cert_file, ca_certs_file), with only the ones passed in being present in the returned
    tuple.
    """
    certs_dir = pathlib.Path(root_dir) / "data" / "certs"
    private_key_file = certs_dir / "client.key"
    local_cert_file = certs_dir / "client.pem"
    ca_certs_file = certs_dir / "ca_certs.pem"

    certs_dir.mkdir(parents=True, exist_ok=True)

    return_values = []
    if private_key:
        private_key_file.write_text(private_key)
        return_values.append(private_key_file)
    if local_cert:
        local_cert_file.write_text(local_cert)
        return_values.append(local_cert_file)
    if ca_certs:
        ca_certs_file.write_text(ca_certs)
        return_values.append(ca_certs_file)

    return tuple(map(str, return_values))
