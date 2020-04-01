# MHS Adaptor Integration Tests

This package contains a the integration tests intended to pre-assure the Message Handling Service and all the
associated services/interfaces used in the Spine messaging. 

## Pre-requisites for Integration Tests

You must first have establish connectivity to an NHS Digital integration testing environment [such as OpenTest](../../setup-opentest.md).

## Running the Integration Tests from PyCharm locally

The term "integration" test here refers to end-to-end testing of the MHS Adaptor through integrating with an NHS Digital 
test environment such as OpenTest. These integration tests cover positive testing scenarios
only.

`pipenv run inttests` will run all integration tests.

When running the tests locally, you will need to set the MHS_ADDRESS, ASID, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, MHS_DYNAMODB_ENDPOINT_URL in the 'Environment variables' section of
 the Run/Debug Configurations.
- The INTEGRATION_TEST_ASID is a 12 digit number needed to access Opentest, supplied by NHS Digital
    - eg INTEGRATION_TEST_ASID=123456789012
- The MHS_ADDRESS is the URL of the MHS instance being used for testing
    - eg MHS_ADDRESS=http://localhost
- The AWS_ACCESS_KEY_ID can be 'test' locally.
- The AWS_SECRET_ACCESS_KEY can be 'test' locally.
- MHS_DYNAMODB_ENDPOINT_URL can be http://localhost:8000 locally.

You will need to complete the setup steps for all the associated services in test prior to running this test suite

## Running the Integration Tests from the Command Line locally

The environment variable described above will need to be present in the environment, using a bash script:

```bash
export MHS_ADDRESS="http://localhost"
export SCR_ADDRESS="http://localhost:9000/"
export INTEGRATION_TEST_ASID="Your NHS Digital assigned ASID here"
export AWS_ACCESS_KEY_ID="test"
export AWS_SECRET_ACCESS_KEY="test"
export MHS_DYNAMODB_ENDPOINT_URL="http://localhost:8000"
```
The URL's above should be those defined in your `docker-compose.yml` file. The script can be executed throught the `source` command.

Run `pipenv run inttests` from this directory.

Note:
If you experience an error `No module name xmlrunner`, you will need to run the command `pip install unittest-xml-reporting`

## Running the Component Tests

Component tests here are defined as integration tests which test the MHS Alpha, integrating with a mocked spine instance
which has been created to enable local negative testing scenarios which are not possible using OpenTest.

`pipenv run componenttests` will run all component tests.

To setup the test environment locally, run the following commands from the root directory:
```bash
./setup_component_test_env.sh
source ./component-test-source.sh
docker-compose -f docker-compose.yml -f docker-compose.component.override.yml -p custom_network up --build
```

## Running scalable docker cluster

By default docker-compose starts 1 instance per service. 
To be able scale up, a load balance has to be added to the cluster, 
target service has to have internal port to ephemeral binding
and and environment variable has to be set for HTTPS comm.

The `docker-compose.lb.override.yml` contains additional definitions for 2 load balancers - inbound + ourbound services.

To run the scalable environment:
1. export env vars (assuming that you have 3 test spine cert files in current folder `cat mhs_client_cert` `cat mhs_client_key` `cat mhs_client_cacerts`)
```
export MHS_INBOUND_QUEUE_URL="rabbitmq:5672/inbound/"
export MHS_SECRET_INBOUND_QUEUE_USERNAME="guest"
export MHS_SECRET_INBOUND_QUEUE_PASSWORD="guest"
export MHS_STATE_TABLE_NAME="mhs_state"
export MHS_SYNC_ASYNC_STATE_TABLE_NAME="sync_async_state"
export MHS_DYNAMODB_ENDPOINT_URL="http://dynamodb:8000"
export AWS_ACCESS_KEY_ID="test"
export AWS_SECRET_ACCESS_KEY="test"
export MHS_SECRET_PARTY_KEY="<party key received from opentest>"
export MHS_SECRET_CLIENT_CERT=`cat mhs_client_cert`
export MHS_SECRET_CLIENT_KEY=`cat mhs_client_key`
export MHS_SECRET_CA_CERTS=`cat mhs_client_cacerts`
```
2. run:
```
docker-compose -f docker-compose.yml -f docker-compose.lb.override.yml stop;
docker-compose -f docker-compose.yml -f docker-compose.lb.override.yml build; 
docker-compose -f docker-compose.yml -f docker-compose.lb.override.yml up
```
3. to scale up run: 
```
docker-compose -f docker-compose.yml -f docker-compose.lb.override.yml scale inbound=3 outbound=3
```

## Running integration tests against fake components

Run `fake_spine` and `fake_spineroutelookup` as if running component tests
Run `inbound` and `outbound` with the `all_component_test_env.yaml` configuration (same as of running component tests)
Run the integration tests using the `all_component_test_env.yaml` instead of the normal integration test configuration.

## Fake Spine request / response delays

There are two environment variables that can control how quickly Fake Spine responds:

* `FAKE_SPINE_OUTBOUND_DELAY_MS` (default: 0) controls the minimum time the service will take to handle each outbound request
* `FAKE_SPINE_INBOUND_DELAY_MS` (default: 0) controls how much time after the outbound request completes that the service will send the asynchronous inbound response