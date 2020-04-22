# Fake Spine

The Fake Spine service mocks the Spine service to provide outbound responses and asynchronous inbound replies for
component and performance testing. 

## Component Testing

There are specific message ids that trigger error responses which are not normally possible to generate on OpenTest. The
file `fake_spine/component_test_responses.py` maps these message ids to their error responses.

## Performance Testing

For any message with a message id not mapped to specific errors (see Component Testing above) an attempt is made to
generate a template response (outbound) and reply (inbound) depending on that message's interaction type. The file
`fake_spine/vnp_test_responses.py` maps the interaction types to the mock responses for the messaging pattern.

| Interaction       | Messaging Pattern | Inbound Reply? |
|-------------------|-------------------|----------------|
| QUPC_IN160101UK05 | Async Express     | Yes            |
| REPC_IN150016UK05 | Async Reliable    | Yes            |
| QUPA_IN040000UK32 | Synchronous       | No             |
| COPC_IN000001UK01 | Forward Reliable  | Yes            |

## Inbound Proxy

The Fake Spine service runs a basic proxy server to handle mutual TLS authentication for requests made to the inbound
service.

## Health Check

The Fake Spine services runs a healthcheck on `/healthcheck`. The healthcheck is always on the same port and URI
scheme used by the outbound request handler.

## Configuration

The service is configured using environment variables. Variables without a default value are *required* to be provided
when the service is run.

| Environment Variable            | Default | Description 
| --------------------------------|---------|-------------
| FAKE_SPINE_PRIVATE_KEY          |         | TLS private key for both HTTPS outbound request handler and inbound mutual TLS
| FAKE_SPINE_CERTIFICATE          |         | TLS certificate for both HTTPS outbound request handler and inbound mutual TLS
| FAKE_SPINE_CA_STORE             |         | CA certificates for both HTTPS outbound request handler and inbound mutual TLS
| FAKE_SPINE_PORT                 | 443     | Port on which the outbound request handler receives requests to fake spine
| INBOUND_PROXY_PORT              | 8888    | Port on which the inbound proxy runs to proxy request made internally to the inbound service
| FAKE_SPINE_PROXY_VALIDATE_CERT  | True    | If "False" then certificate validation errors on requests made to inbound are ignored
| INBOUND_SERVER_BASE_URL         |         | The url (including URI scheme) to which the inbound proxy makes requests (example: https://inbound/)
| FAKE_SPINE_OUTBOUND_DELAY_MS    | 0       | To simulate actual Spine response times, the number of milliseconds to wait before returning an outbound response
| FAKE_SPINE_INBOUND_DELAY_MS     | 0       | To simulate actual Spine asynchronous response times, the number of milliseconds to wait before sending a reply to the inbound service
| MHS_SECRET_PARTY_KEY            |         | The party key (recipient) used to make request to inbound. *Must* match the party key used to configure the inbound service
| FAKE_SPINE_OUTBOUND_SSL_ENABLED | True    | If "False" then the outbound request handler will use HTTP instead of HTTPS
| MHS_LOG_LEVEL                   |         | The desired logging level

## Running

### Docker

From the repository root, first ensure the base images are built:

`$ ./build.sh`

Then run docker-compose:

`$ BUILD_TAG=latest docker-compose -f docker-compose.yml -f docker-compose.component.override.yml up`

### Locally

`$ pipenv start`

### For Component Tests

The `integration-tests/all_component_test_env.yaml` configuration can be used for component testing as described in
`integration-tests/integration_tests/README.md`
