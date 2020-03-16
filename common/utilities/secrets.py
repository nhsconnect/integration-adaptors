"""
Secrets

This module holds the secret config used by an application. To use this module, first
call `setup_secrets_config` to populate `secret_config`. Then, just get any required config
using `get_secret_config` (or directly use `secret_config` for more complex use cases).
"""
import logging
import os
from typing import Dict, Optional

secret_config: Dict[str, str] = {}


def setup_secret_config(component_name: str):
    """
    Populate the `secret_config` variable in this module

    :param component_name: name of the component, used to find the relevant
    environment variables to populate `secret_config` with.
    """
    prefix = component_name + "_SECRET_"
    for k, v in os.environ.items():
        if k.startswith(prefix):
            secret_config[k[len(prefix):]] = v


_config_default = object()


def get_secret_config(key: str, default: Optional[str] = _config_default) -> str:
    """
    Get secret config variable or error out (and log the error)

    :param key: key to lookup
    :param default: default value to return if none is found
    :return: the secret config variable
    """

    if key in secret_config:
        # Can't use IntegrationAdaptorsLogger due to circular dependency
        logging.info(f'Obtained secret config ConfigName="{key}"')
        return secret_config[key]
    elif default is not _config_default:
        logging.info(f'Failed to get secret config ConfigName="{key}". Returning a default value.')
        return default
    else:
        # Can't use IntegrationAdaptorsLogger due to circular dependency
        logging.error(f'Failed to get secret config ConfigName="{key}"')
        raise KeyError
