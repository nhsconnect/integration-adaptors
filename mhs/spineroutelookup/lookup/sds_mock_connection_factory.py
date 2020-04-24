import json
import os
import shutil
from urllib.parse import urlparse, ParseResult
import argparse
import boto3
from ldap3 import Server, Connection, ALL, ALL_ATTRIBUTES, MOCK_ASYNC
import sys

from utilities import config, integration_adaptors_logger as log

logger = log.IntegrationAdaptorsLogger(__name__)

LDAP_MOCK_DATA_URL_CONFIG_KEY = 'LDAP_MOCK_DATA_URL'
FAKE_SPINE_URL_CONFIG_KEY = 'FAKE_SPINE_URL'

_MOCK_DATA_BASE_PATH = 'mock_ldap_data'
_SERVER_INFO_FILE = 'server_info.json'
_SERVER_SCHEMA_FILE = 'server_schema.json'
_SERVER_ENTRIES_FILE = 'server_entries.json'

_MOCK_DATA_SERVER_INFO_FILE_PATH = os.path.join(_MOCK_DATA_BASE_PATH, _SERVER_INFO_FILE)
_MOCK_DATA_SERVER_SCHEMA_FILE_PATH = os.path.join(_MOCK_DATA_BASE_PATH, _SERVER_SCHEMA_FILE)
_MOCK_DATA_SERVER_ENTRIES_FILE_PATH = os.path.join(_MOCK_DATA_BASE_PATH, _SERVER_ENTRIES_FILE)


def _file_mock_data_loader(parsed_url: ParseResult) -> None:
    src_file_base_path = "/" + parsed_url.netloc + parsed_url.path

    file_names = [_SERVER_INFO_FILE, _SERVER_SCHEMA_FILE, _SERVER_ENTRIES_FILE]

    for file_name in file_names:
        src_file_path = os.path.join(src_file_base_path, file_name)
        dest_file_path = os.path.join(_MOCK_DATA_BASE_PATH, file_name)
        logger.info("Copying file from '%s' to '%s'", src_file_path, dest_file_path)
        shutil.copyfile(src_file_path, dest_file_path)


def _s3_mock_data_loader(parsed_url: ParseResult) -> None:
    aws_profile = config.get_config('AWS_PROFILE', default=None)

    bucket_name = parsed_url.netloc
    key_base = parsed_url.path[1:]

    session = boto3.Session(profile_name=aws_profile)
    s3 = session.client('s3')

    file_names = [_SERVER_INFO_FILE, _SERVER_SCHEMA_FILE, _SERVER_ENTRIES_FILE]
    for file_name in file_names:
        src_file_path = os.path.join(key_base, file_name)
        dest_file_path = os.path.join(_MOCK_DATA_BASE_PATH, file_name)
        logger.info("Downloading S3 file from '%s' to '%s'", src_file_path, dest_file_path)
        s3.download_file(bucket_name, src_file_path, dest_file_path)


_MOCK_DATA_LOADERS = {
    'file': _file_mock_data_loader,
    's3': _s3_mock_data_loader,
}


def _modify_spine_url(fake_spine_url):
    logger.info("Modifying spine url to '%s'", fake_spine_url)
    with open(_MOCK_DATA_SERVER_ENTRIES_FILE_PATH, 'r') as json_file:
        data = json.load(json_file)

    for entry in data['entries']:
        if 'attributes' in entry:
            attributes = entry['attributes']
            if 'nhsMHSEndPoint' in attributes:
                attributes['nhsMHSEndPoint'] = [fake_spine_url]
            if 'nhsMhsFQDN' in attributes:
                attributes['nhsMhsFQDN'] = fake_spine_url
        if 'raw' in entry:
            raw = entry['raw']
            if 'nhsMHSEndPoint' in raw:
                raw['nhsMHSEndPoint'] = [fake_spine_url]
            if 'nhsMhsFQDN' in raw:
                raw['nhsMhsFQDN'] = fake_spine_url

    with open(_MOCK_DATA_SERVER_ENTRIES_FILE_PATH, 'w') as json_file:
        json.dump(data, json_file, indent=4)


def build_mock_sds_connection():
    url = config.get_config(LDAP_MOCK_DATA_URL_CONFIG_KEY)
    parsed_url = urlparse(url)

    _MOCK_DATA_LOADERS[parsed_url.scheme](parsed_url)

    fake_spine_url = config.get_config(FAKE_SPINE_URL_CONFIG_KEY, default=None)
    if fake_spine_url:
        _modify_spine_url(fake_spine_url)
    else:
        logger.info("Skipping spine url modification as config key '%s' is not present", FAKE_SPINE_URL_CONFIG_KEY)

    fake_server = Server.from_definition(
        'fake_server',
        _MOCK_DATA_SERVER_INFO_FILE_PATH,
        _MOCK_DATA_SERVER_SCHEMA_FILE_PATH)
    fake_connection = Connection(fake_server, client_strategy=MOCK_ASYNC)
    fake_connection.strategy.entries_from_json(_MOCK_DATA_SERVER_ENTRIES_FILE_PATH)
    fake_connection.bind()
    return fake_connection


def main(args):
    config.setup_config('MHS')
    log.configure_logging('spineroutelookup')
    _read_real_server_data(args.path, args.nhs_id_code)


def _read_real_server_data(output_path, nhs_id_code):
    ldap_address = config.get_config('SDS_URL')
    logger.info("Downloading real server data from '%s' for nhs id code '%s' and saving data at '%s'",
                ldap_address, nhs_id_code, output_path)
    server = Server(ldap_address, get_info=ALL)
    connection = Connection(server, auto_bind=True)

    server_info_path = os.path.join(output_path, _SERVER_INFO_FILE)
    logger.info("Saving real server info at '%s'", server_info_path)
    server.info.to_file(server_info_path)

    server_schema_path = os.path.join(output_path, _SERVER_SCHEMA_FILE)
    logger.info("Saving real server schema at '%s'", server_schema_path)
    server.schema.to_file(server_schema_path)

    if connection.search('ou=Services,o=nhs', f'(nhsIDCode={nhs_id_code})', attributes=ALL_ATTRIBUTES):
        server_entries_path = os.path.join(output_path, _SERVER_ENTRIES_FILE)
        logger.info("Saving server entries at '%s'", server_entries_path)
        connection.response_to_file(server_entries_path, raw=True)
    else:
        logger.error("LDAP search yield no results")

    connection.unbind()


class ArgParser(argparse.ArgumentParser):
    def error(self, message):
        sys.stderr.write('error: %s\n' % message)
        self.print_help()
        sys.exit(2)


if __name__ == "__main__":
    parser = ArgParser(description='Downloads real LDAP server config')
    parser.add_argument('path', help="Path where to download files")
    parser.add_argument('nhs_id_code', help="NHS ID Code do download data for")
    app_args = parser.parse_args()

    try:
        main(app_args)
    except Exception:
        parser.print_help()
        logger.critical('Fatal exception in main application', exc_info=True)
    finally:
        logger.info('Exiting application')
