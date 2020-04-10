import os


class ConfigurationException(Exception):
    pass


def environ_or_error(key: str, default: str = None) -> str:
    value = os.environ.get(key, default)
    if value is None:
        raise ConfigurationException(f'The environment variable {key} is required.')
    return value


ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
FAKE_SPINE_PRIVATE_KEY = environ_or_error('FAKE_SPINE_PRIVATE_KEY')
FAKE_SPINE_CERTIFICATE = environ_or_error('FAKE_SPINE_CERTIFICATE')
FAKE_SPINE_CA_STORE = environ_or_error('FAKE_SPINE_CA_STORE')
FAKE_SPINE_PORT = int(environ_or_error('FAKE_SPINE_PORT', default='443'))
INBOUND_PROXY_PORT = int(environ_or_error('INBOUND_PROXY_PORT', default='8888'))
INBOUND_SERVER_BASE_URL = environ_or_error('INBOUND_SERVER_BASE_URL')
OUTBOUND_DELAY_MS = int(environ_or_error('FAKE_SPINE_OUTBOUND_DELAY_MS', default='0'))
INBOUND_DELAY_MS = int(environ_or_error('FAKE_SPINE_INBOUND_DELAY_MS', default='0'))
MHS_SECRET_PARTY_KEY = os.environ.get('MHS_SECRET_PARTY_KEY')
FAKE_SPINE_HEALTHCHECK_PORT = int(os.environ.get('FAKE_SPINE_HEALTHCHECK_PORT', default='80'))
