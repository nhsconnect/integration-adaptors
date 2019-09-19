"""
Config

This module holds the config used by an application. To use this module, first
call `setup_config` to populate `config`. Then, just get any required config
using `get_config` (or directly use `config` for more complex use cases).
"""
import logging
import os
from typing import Dict, Optional

config: Dict[str, str] = {}

_LOG_TAG = 'CONFIG'


def setup_config(component_name: str):
    """
    Populate the `config` variable in this module

    :param component_name: name of the component, used to find the relevant
    environment variables to populate `config` with.
    """
    prefix = component_name + "_"
    for k, v in os.environ.items():
        if k.startswith(prefix):
            config[k[len(prefix):]] = v


_config_default = object()


def get_config(key: str, default: Optional[str] = _config_default) -> str:
    """
    Get config variable or error out (and log the error)

    :param key: key to lookup
    :param default: default value to return if none is found
    :return: the config variable
    """

    if key in config:
        # Can't use IntegrationAdaptorsLogger due to circular dependency
        logging.info(f'Obtained config ConfigName:"{key}" ConfigValue:"{config[key]}" ProcessKey={_LOG_TAG}001')
        return config[key]
    elif default is not _config_default:
        logging.info(f'Failed to get config ConfigName:"{key}". Returning DefaultValue:"{default}". '
                     f'ProcessKey={_LOG_TAG}002')
        return default
    else:
        logging.error(f'Failed to get config ConfigName:"{key}" ProcessKey={_LOG_TAG}003')
        raise KeyError
