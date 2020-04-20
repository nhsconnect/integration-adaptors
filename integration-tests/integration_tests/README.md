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

## Running Integration Tests with Visual Studio Code Rest Client
#### Prerequisites
The following is required
- Visual Studio Code
- Visual Studio Code REST Client Plugin: https://marketplace.visualstudio.com/items?itemName=humao.rest-client
- Docker 
- OpenTest connection

#### Environment set up
1. Create a docker-compose.yml file in a local folder with the following content:

```yml
version: '3' 

services: 
  inbound: 
    image: nhsdev/nia-mhs-inbound:${BUILD_TAG} 
    ports: 
      - "443" 
      - "80" 
    environment: 
      - MHS_LOG_LEVEL=NOTSET 
      - MHS_SECRET_PARTY_KEY 
      - MHS_SECRET_CLIENT_CERT 
      - MHS_SECRET_CLIENT_KEY 
      - MHS_SECRET_CA_CERTS 
      - MHS_INBOUND_QUEUE_URL=rabbitmq:5672/inbound 
      - MHS_SECRET_INBOUND_QUEUE_USERNAME=guest 
      - MHS_SECRET_INBOUND_QUEUE_PASSWORD=guest 
      - MHS_STATE_TABLE_NAME=mhs_state 
      - MHS_SYNC_ASYNC_STATE_TABLE_NAME=sync_async_state 
      - MHS_DYNAMODB_ENDPOINT_URL=http://dynamodb:8000 
      # boto3 requires some AWS creds to be provided, even 
      # when connecting to local DynamoDB 
      - AWS_ACCESS_KEY_ID=test 
      - AWS_SECRET_ACCESS_KEY=test 
      - TCP_PORTS=443 
      - SERVICE_PORTS=443,80 

  outbound: 
    image: nhsdev/nia-mhs-outbound:${BUILD_TAG} 
    ports: 
      - "80" 
    environment: 
      - MHS_LOG_LEVEL=NOTSET 
      - MHS_SECRET_PARTY_KEY 
      - MHS_SECRET_CLIENT_CERT 
      - MHS_SECRET_CLIENT_KEY 
      - MHS_SECRET_CA_CERTS 
      - MHS_STATE_TABLE_NAME=mhs_state 
      - MHS_DYNAMODB_ENDPOINT_URL=http://dynamodb:8000 
      - MHS_SYNC_ASYNC_STATE_TABLE_NAME=sync_async_state 
      - AWS_ACCESS_KEY_ID=test 
      - AWS_SECRET_ACCESS_KEY=test 
      - MHS_RESYNC_INTERVAL=1 
      - MAX_RESYNC_RETRIES=20 
      - MHS_SPINE_ROUTE_LOOKUP_URL=http://route 
      - MHS_SPINE_ORG_CODE=YES 
      - MHS_SPINE_REQUEST_MAX_SIZE=4999600 # 5 000 000 - 400 
      # Note that this endpoint URL is Opentest-specific 
      - MHS_FORWARD_RELIABLE_ENDPOINT_URL=https://192.168.128.11/reliablemessaging/forwardreliable 
      - SERVICE_PORTS=80 
      - MHS_OUTBOUND_VALIDATE_CERTIFICATE

  route: 
    image: nhsdev/nia-mhs-route:${BUILD_TAG} 
    ports: 
        - "8080:80" 
    environment: 
      - MHS_LOG_LEVEL=NOTSET 
      - MHS_SDS_URL=ldap://192.168.128.11 
      - MHS_SDS_SEARCH_BASE=ou=services,o=nhs 
      - MHS_DISABLE_SDS_TLS=True 
      - MHS_SDS_REDIS_CACHE_HOST=redis 
      - MHS_SDS_REDIS_DISABLE_TLS=True 
  dynamodb: 
    image: nhsdev/nia-dynamodb-local:1.0.1 
    ports: 
      - "8000:8000" 
  rabbitmq: 
    image: nhsdev/nia-rabbitmq-local:1.0.1  
    ports: 
      - "15672:15672" 
      - "5672:5672" 
    hostname: "localhost" 
  redis: 
    image: redis 
    ports: 
      - "6379:6379" 

  inbound-lb: 
    image: dockercloud/haproxy 
    links: 
      - inbound 
    ports: 
      - "443:443" 
      - "8079:80" 
    volumes: 
      - /var/run/docker.sock:/var/run/docker.sock 
    environment:  
      - MODE=tcp 
      - TIMEOUT=connect 0, client 0, server 0
```

2. Create a script to start the containers, call it export-env-vars-and-run-mhs-docker.sh and make it executable.

3. Add the following content and your OpenTest details into the file

```bash
LIGHT_GREEN='\033[1;32m' 
NC='\033[0m' 
echo -e "${LIGHT_GREEN}Exporting environment variables${NC}" 

export BUILD_TAG="latest" 
export MHS_OUTBOUND_VALIDATE_CERTIFICATE="False"

# Your OpenTest Party key here 
export MHS_SECRET_PARTY_KEY="" 

# Your OpenTest endpoint certificate here 
export MHS_SECRET_CLIENT_CERT="" 

# Your OpenTest endpoint private key here 
export MHS_SECRET_CLIENT_KEY="" 

# OpenTest Endpoint issuing subCA certificate and Root CA certificate here 
export MHS_SECRET_CA_CERTS="" 

echo -e "${LIGHT_GREEN}Stopping running containers${NC}" 
docker-compose -f docker-compose.yml stop; 

echo -e "${LIGHT_GREEN}Build and starting containers${NC}" 
docker-compose -f docker-compose.yml up -d --build
```

4. Confirm you are connected to the OpenTest VPN and start all the containers by executing the shell script you created above.

./export-env-vars-and-run-mhs-docker.sh

#### Executing requests in Visual Studio Code
1. Open Visual Studio Code
2. Check out the integration-adapter project on the develop branch from github: https://github.com/nhsconnect/integration-adaptors
3. In the project root create the directory `.vscode` if it doesn't exist already
4. In the .vscode folder create a file called `settings.json`
5. Add the information below to the `settings.json` file
    ```json
    {
        "workbench.settings.editor": "json",
        "workbench.settings.useSplitJSON": true,
        "rest-client.environmentVariables": {
            "$shared": {},
            "$mhs": {
                "BASE_URL": "http://localhost",
                "INBOUND-PORT": "8082",
                "OUTBOUND-PORT": "80",
                "ROUTE-LOOKUP-PORT": "8088",
                "FAKE-SPINE-PORT": "8091",
                "ASID": "9XXXXXXXXXXX",
                "PARTY-KEY": "A9XXXX-XXXXXXX"
            }
        }
    }
    ```

6. Navigate the code directories to the requests: `/http-client/mhs/outbound`
7. Navigate to the folder of the message pattern type you wish to run a request for and open a request .http file
8. In the bottom right corner of Visual Studio Code click `No Environment` and select `$mhs`
9. Change the data `@PATIENT_NHS_NUMBER` to be a number which is valid in OpenTest. A correct number can be found in the
correct integration test for the same message pattern type. 

    The integration tests can be found in `/integration-tests/integration_tests/integration_tests/end_to_end_tests`

    The number can be found as the second parameter in a line which looks like this `message, message_id = build_message('QUPC_IN160101UK05', '9689177923')`

10. Click the `Send Request` link which can be found inside the .http file request

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