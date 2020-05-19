import os


def environ_or_error(key: str, default: str = None) -> str:
    value = os.environ.get(key, default)
    if value is None:
        raise ConfigurationException(f'The environment variable {key} is required.')
    return value


def str2bool(value):
    if value.lower() == str(True).lower():
        return True
    elif value.lower() == str(False).lower():
        return False
    else:
        raise ValueError(f"Unable to parse '{value}'")


class ConfigurationException(Exception):
    pass


class FakeSpineConfiguration(object):
    def __init__(self):
        self.ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
        self.FAKE_SPINE_PRIVATE_KEY = environ_or_error('FAKE_SPINE_PRIVATE_KEY')
        self.FAKE_SPINE_CERTIFICATE = environ_or_error('FAKE_SPINE_CERTIFICATE')
        self.FAKE_SPINE_CA_STORE = environ_or_error('FAKE_SPINE_CA_STORE')
        self.FAKE_SPINE_PORT = int(environ_or_error('FAKE_SPINE_PORT', default='443'))
        self.INBOUND_PROXY_PORT = int(environ_or_error('INBOUND_PROXY_PORT', default='8888'))
        self.FAKE_SPINE_PROXY_VALIDATE_CERT = str2bool(os.environ.get('FAKE_SPINE_PROXY_VALIDATE_CERT', default='True'))
        self.INBOUND_SERVER_BASE_URL = environ_or_error('INBOUND_SERVER_BASE_URL')
        self.OUTBOUND_DELAY_MS = int(environ_or_error('FAKE_SPINE_OUTBOUND_DELAY_MS', default='0'))
        self.INBOUND_DELAY_MS = int(environ_or_error('FAKE_SPINE_INBOUND_DELAY_MS', default='0'))
        self.MHS_SECRET_PARTY_KEY = os.environ.get('MHS_SECRET_PARTY_KEY')
        self.FAKE_SPINE_OUTBOUND_SSL_ENABLED = str2bool(os.environ.get('FAKE_SPINE_OUTBOUND_SSL_ENABLED', default='True'))
