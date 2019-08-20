import enum
import os
from operator import itemgetter
from typing import List, Generator

import boto3

from definitions import ROOT_DIR


class Component(enum.Enum):
    MHS = enum.auto()
    SCR = enum.auto()


_component_log_group_name_map = {
    Component.MHS: "/ecs/test-environment",
    Component.SCR: "/ecs/scr-service-environment",
}

_component_log_filename_map = {
    Component.MHS: "mhs.txt",
    Component.SCR: "scr.txt"
}


def get_logs(component: Component) -> Generator:
    if os.environ.get("MHS_ADDRESS", "localhost") == "localhost":
        return _get_logs_from_file(component)
    return _get_logs_from_aws_cloud_watch(component)


def _get_logs_from_file(component: Component) -> Generator:
    yield from open(os.path.join(ROOT_DIR, "log_files", _component_log_filename_map[component]))


# Deprecated
def __get_logs_from_aws_cloud_watch(log_group_name: Component) -> List:
    log_stream_name_prefix = os.environ.get("BUILD_TAG", None)

    log_streams = _client.describe_log_streams(
        logGroupName=log_group_name,
        logStreamNamePrefix=log_stream_name_prefix
    )["logStreams"]
    assert len(log_streams) == 1
    log_stream_name = log_streams[0]["logStreamName"]

    log_events = _client.get_log_events(
        logGroupName=log_group_name, logStreamName=log_stream_name
    )["events"]
    return list(map(itemgetter("message"), log_events))


def _get_logs_from_aws_cloud_watch(component: Component) -> Generator:
    log_group_name = _component_log_group_name_map[component]
    log_prefix = os.environ.get("BUILD_TAG", None)

    aws_client = boto3.client(service_name="logs",
                              region_name="eu-west-2")

    next_token = None
    while True:
        if next_token is None:
            log_streams = aws_client.describe_log_streams(logGroupName=log_group_name,
                                                          logStreamNamePrefix=log_prefix)
        else:
            log_streams = aws_client.describe_log_streams(logGroupName=log_group_name,
                                                          logStreamNamePrefix=log_prefix,
                                                          nextToken=next_token)
        next_token = log_streams["nextToken"]
        streams = log_streams["logStreams"]
        print(next_token)

        for stream in streams:
            log_stream_name = stream["logStreamName"]
            log_events = aws_client.get_log_events(logGroupName=log_group_name, logStreamName=log_stream_name)["events"]
            yield from [event['message'] for event in log_events]

        if next_token is None:
            break


if __name__ == '__main__':
    for i in get_logs(Component.MHS):
        print(i)
