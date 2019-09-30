#!/bin/bash

# This script is to be run inside a python docker container to run our component tests in CI.
# The reason this is not a Dockerfile is because currently the integration tests project reference common at the root
# level of the solution, and i dont want to add a Dockfile to the root of the project to get this to build.

# in order to use this script run:
# docker run --network custom_network_default -v $PWD:/test --entrypoint /test/integration-tests/run_component_tests.sh python:3-slim
set -e
apt-get update
apt-get install -y build-essential libssl-dev swig pkg-config
pip install pipenv
(cd /test/integration-tests/integration_tests || exit; pipenv install --dev --deploy --ignore-pipfile)

export MHS_ADDRESS="outbound"
(cd /test/integration-tests/integration_tests || exit; pipenv run componenttests)
