# This file is used to run component tests on CI. Once the component tests don't rely on the common project, this
# file can be moved to a sub directory.
FROM python:3.7-slim

RUN apt-get update
RUN apt-get install -y build-essential libssl-dev swig pkg-config
RUN pip install pipenv

WORKDIR /test
COPY . .

WORKDIR /test/integration-tests/integration_tests
RUN pipenv install --dev --deploy --ignore-pipfile

ENTRYPOINT [ "pipenv", "run", "componenttests" ]