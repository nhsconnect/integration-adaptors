"""
Config

This module holds the config used by an application. To use this module, first
call `setup_config` to populate `config`. Then, just get any required config
from `config`.
"""
import os
from typing import Dict

config: Dict[str, str] = {}


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
