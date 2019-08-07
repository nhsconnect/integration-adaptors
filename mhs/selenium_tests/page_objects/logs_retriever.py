import enum
import os
import pathlib
from operator import itemgetter
from typing import List

import boto3

from definitions import ROOT_DIR

_client = boto3.client('logs', region_name='eu-west-2')


class Component(enum.Enum):
    MHS = enum.auto()
    SCR = enum.auto()


_component_log_group_name_map = {
    Component.MHS: '/ecs/test-environment',
    Component.SCR: '/ecs/scr-service-environment'
}

_component_log_filename_map = {
    Component.MHS: 'mhs.txt',
    Component.SCR: 'scr.txt'
}


def get_logs(component: Component) -> List[str]:
    if os.environ.get('MHS_ADDRESS', 'localhost') == 'localhost':
        return _get_logs_from_file(component)
    return _get_logs_from_cloudwatch(component)


def _get_logs_from_cloudwatch(log_group_name):
    log_stream_name_prefix = os.environ.get('BUILD_TAG', None)

    log_streams = _client.describe_log_streams(
        logGroupName=log_group_name, logStreamNamePrefix=log_stream_name_prefix
    )['logStreams']
    assert len(log_streams) == 1
    log_stream_name = log_streams[0]['logStreamName']

    log_events = _client.get_log_events(logGroupName=log_group_name, logStreamName=log_stream_name)['events']
    return list(map(itemgetter('message'), log_events))


def _get_logs_from_file(component: Component):
    with (pathlib.Path(ROOT_DIR) / 'log_files' / _component_log_filename_map[component]).open() as f:
        return list(f)
