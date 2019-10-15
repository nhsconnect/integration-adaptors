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