from pathlib import Path

from ldap3 import Server, Connection, MOCK_ASYNC
import mhs.routing.sds as sds
from definitions import ROOT_DIR

MHS_TEST_DATA_PATH = Path(ROOT_DIR) / 'mhs' / 'routing' / 'tests' / 'data'
SERVER_INFO_PATH = str(MHS_TEST_DATA_PATH / 'my_real_server_info.json')
SCHEMA_PATH = str(MHS_TEST_DATA_PATH / 'my_real_server_schema.json')
SERVER_ENTRIES_PATH = str(MHS_TEST_DATA_PATH / 'my_real_server_entries.json')


def fake_ldap_server():
    fake_server = Server.from_definition('my_fake_server',
                                         SERVER_INFO_PATH,
                                         SCHEMA_PATH)

    # Create a MockSyncStrategy connection to the fake server
    fake_connection = Connection(fake_server, client_strategy=MOCK_ASYNC)

    # Populate the DIT of the fake server
    fake_connection.strategy.entries_from_json(SERVER_ENTRIES_PATH)

    fake_connection.bind()

    return fake_connection


def mocked_sds_client():
    client = sds.SDSClient()
    connection = fake_ldap_server()
    client.connection = connection
    return client
