import logging
import pathlib
import ssl
from typing import Tuple

import tornado.httpserver
import tornado.ioloop
import tornado.web

import definitions
import request.handler as async_request_handler
import utilities.config as config
import utilities.file_utilities as file_utilities

ASYNC_TIMEOUT = 30


def load_certs(certs_dir: pathlib.Path) -> Tuple[str, str]:
    """Load the necessary TLS certificates from the specified directory.

    :param certs_dir: The directory to load certificates from.
    :return: A tuple consisting of the file names of the client's certificates file, and the client's key.
    """
    certs_file = str(certs_dir / "client.pem")
    key_file = str(certs_dir / "client.key")

    return certs_file, key_file


def load_party_key(data_dir: pathlib.Path) -> str:
    """Load this MHS's party key from the specified directory.

    :param data_dir: The directory to load the party key from.
    :return: The party key to use to identify this MHS.
    """
    party_key_file = str(data_dir / "party_key.txt")
    party_key = file_utilities.FileUtilities.get_file_string(party_key_file)

    assert party_key
    return party_key


def configure_logging() -> None:
    """Configure logging for this application."""
    logging.basicConfig(format="%(asctime)s - %(levelname)s: %(message)s", level=config.config["LOG_LEVEL"])


def start_inbound_server(certs_file: str, key_file: str,  party_key: str) -> None:
    """

    :param certs_file: The filename of the certificate to be used to identify this MHS to a remote MHS.
    :param key_file: The filename of the private key for the certificate identified by certs_file.
    :param workflow: The workflow to be used to handle messages.
    :param party_key: The party key to use to identify this MHS.
    """
    callbacks = {}

    inbound_application = tornado.web.Application(
        [(r"/.*", async_request_handler.InboundHandler, dict(callbacks=callbacks, party_id=party_key))])
    inbound_server = tornado.httpserver.HTTPServer(inbound_application,
                                               ssl_options=dict(certfile=certs_file, keyfile=key_file,
                                                                cert_reqs=ssl.CERT_REQUIRED,
                                                                ca_certs=certs_file))
    inbound_server.listen(443)

    logging.info("Starting inbound server")
    tornado.ioloop.IOLoop.current().start()


def main():
    config.setup_config("MHS")
    configure_logging()

    data_dir = pathlib.Path(definitions.ROOT_DIR) / "data"
    certs_dir = data_dir / "certs"
    certs_file, key_file = load_certs(certs_dir)
    party_key = load_party_key(certs_dir)

    start_inbound_server(certs_file, key_file, party_key)


if __name__ == "__main__":
    main()
