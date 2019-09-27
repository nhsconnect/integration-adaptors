from pathlib import Path

import ldap3

import lookup.sds_client as sds_client
from definitions import ROOT_DIR

MHS_TEST_DATA_PATH = Path(ROOT_DIR) / 'lookup' / 'tests' / 'data'
SERVER_INFO_PATH = str(MHS_TEST_DATA_PATH / 'my_real_server_info.json')
SCHEMA_PATH = str(MHS_TEST_DATA_PATH / 'my_real_server_schema.json')
SERVER_ENTRIES_PATH = str(MHS_TEST_DATA_PATH / 'my_real_server_entries.json')

NHS_SERVICES_BASE = "ou=services,o=nhs"


def fake_ldap_connection() -> ldap3.Connection:
    fake_server = ldap3.Server.from_definition('my_fake_server',
                                               SERVER_INFO_PATH,
                                               SCHEMA_PATH)

    # Create a MockSyncStrategy connection to the fake server
    fake_connection = ldap3.Connection(fake_server, client_strategy=ldap3.MOCK_ASYNC)

    # Populate the DIT of the fake server
    fake_connection.strategy.entries_from_json(SERVER_ENTRIES_PATH)

    fake_connection.bind()

    return fake_connection


def mocked_sds_client():
    return sds_client.SDSClient(fake_ldap_connection(), NHS_SERVICES_BASE)
