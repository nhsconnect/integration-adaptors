# MHS

This package contains a pre-assured implementation of a Message Handling Service (MHS), intended to encapsulate the
details of Spine messaging and provide a simple interface to allow HL7 messages to be sent to a remote MHS.

**WARNING: Verification of the server certificate received when making a connection to a remote MHS is currently
DISABLED (see the [OutboundTransmission](./outbound/outbound/transmission/outbound_transmission.py) class'
`make_request` method).** This MHS should not be used in a production environment unless this certificate verification
is re-enabled.

## Setup
You'll need to have a connection to Spine. For testing purposes, you can use [Opentest](https://nhs-digital-opentest.github.io/Welcome/index.html).

Finally, ensure you have [Pipenv](https://docs.pipenv.org/en/latest/) installed and on your path, then within each of
the subfolders `common`, `inbound` and `outbound` in this directory, run:
```
pipenv install
```

### Developer Setup
To prepare a development environment for this application, ensure you have [Pipenv](https://docs.pipenv.org/en/latest/)
installed and on your path, then within each of the subfolders `common`, `inbound` and `outbound` in this directory, run:
```
pipenv install --dev
```

If the build fails due to dependency issues with proton, follow these instructions:
1) Visit: https://visualstudio.microsoft.com/downloads/
2) Download the 'Community Edition'
3) Run the installer once the download has completed
4) Select the **Desktop development with C++** workload option
5) Once the installation has completed you may have to reboot.


## Running MHS
MHS is made up of multiple components, and running them all separately can be tedious. Instead, use Docker Compose, see [here](../README.md) for how to do this.

### Environment Variables
MHS takes a number of environment variables when it is run. These are:
* `MHS_LOG_LEVEL` This is required to be set to one of: `INFO`, `WARNING`, `ERROR` or `CRITICAL`, where `INFO` displays
the most logs and `CRITICAL` displays the least. Note: Setting this value to one of the more detailed 'standard' Python
log levels (such as `DEBUG` or `NOTSET`) may result in the libraries used by this application logging details that
contain sensitive information such as the content of messages being sent.
* `MHS_SECRET_PARTY_KEY` (inbound & outbound only) The party key associated with your MHS.
* `MHS_SECRET_CLIENT_CERT` Your endpoint certificate
* `MHS_SECRET_CLIENT_KEY` Your endpoint private key
* `MHS_SECRET_CA_CERTS` Should include the following in this order: endpoint issuing subCA certificate, root CA Certificate.
* `MHS_STATE_TABLE_NAME` (inbound & outbound only) The name of the DynamoDB table used to store MHS state.
* `MHS_SYNC_ASYNC_STATE_TABLE_NAME` (inbound & outbound only) The table name used to store sync async responses
* `MHS_STATE_STORE_MAX_RETRIES'` (inbound & outbound only) The max number of retries when attempting to interact with either the work description or sync-async store. Defaults to `3`
* `MHS_OUTBOUND_TRANSMISSION_MAX_RETRIES` (outbound only) This is the maximum number of retries for outbound requests. If no value is given a default of `3` is used.
* `MHS_OUTBOUND_TRANSMISSION_RETRY_DELAY` (outbound only) The delay between retries of outbound requests in milliseconds. If no value is given, a default of `100` is used.
* `MHS_OUTBOUND_HTTP_PROXY` (outbound only) An optional http(s) proxy to route downstream requests via. Note that the proxy must passthrough https requests transparently.
* `MHS_OUTBOUND_HTTP_PROXY_PORT` (outbound only) The http(s) proxy port to use. Ignored if `MHS_OUTBOUND_HTTP_PROXY` is not provided. Defaults to `3128`.
* `MHS_INBOUND_QUEUE_URL` (inbound only) The host url of the amqp inbound queue broker. e.g. `amqps://example.com:port/queue-name`. Note that if the amqp connection being used is a secured connection (which it should be in production), then the url should start with `amqps://` and not `amqp+ssl://`.
* `MHS_SECRET_INBOUND_QUEUE_USERNAME` (inbound only) The username to use when connecting to the amqp inbound queue.
* `MHS_SECRET_INBOUND_QUEUE_PASSWORD` (inbound only) The password to use when connecting to the amqp inbound queue.
* `MHS_INBOUND_QUEUE_MAX_RETRIES` (inbound only) The max number of times to retry putting a message onto the amqp inbound queue. Defaults to `3`.
* `MHS_INBOUND_QUEUE_RETRY_DELAY` (inbound only) The delay in milliseconds between retrying putting a message onto the amqp inbound queue. Defaults to `100`ms.
* `MHS_SYNC_ASYNC_STORE_MAX_RETRIES'` (inbound only) The max number of retries when attempting to add a message to the sync-async store. Defaults to `3`
* `MHS_SYNC_ASYNC_STORE_RETRY_DELAY` (inbound only) The delay in milliseconds between retrying placing a message on the sysnc-async store. Defaults to `100`ms
* `MHS_RESYNC_RETRIES` (outbound only) The total number of attempts made to the sync-async store during resynchronisation, defaults to `20`
* `MHS_RESYNC_INTERVAL` (outbound only) The time in between polls of the sync-async store, the interval is in seconds and defaults to `1`
* `MHS_SPINE_ROUTE_LOOKUP_URL` (outbound only) The URL of the Spine route lookup service. E.g `https://example.com`. This URL should not contain path or query parameter parts.
* `MHS_SPINE_ORG_CODE` (outbound only) The organisation code for the Spine instance that your MHS is communicating with. E.g `YES`
* `MHS_SDS_URL` (Spine Route Lookup service only) The URL to communicate with SDS on. e.g. `ldaps://example.com`
* `MHS_DISABLE_SDS_TLS` (Spine Route Lookup service only) An optional flag that can be set to disable TLS for SDS
connections. *Must* be set to exactly `True` for TLS to be disabled.
* `MHS_SDS_CACHE_EXPIRY_TIME` (Spine Route Lookup service only). An optional value that specifies the time (in seconds)
that a value should be held in the SDS cache. Defaults to `900` (fifteen minutes)
* `MHS_SDS_REDIS_CACHE_HOST` (Spine Route Lookup service only). The Redis host to use when caching SDS information
retrieved from SDS.
* `MHS_SDS_REDIS_CACHE_PORT` (Spine Route Lookup service only). An optional value that specified the port to use when
connecting to the Redis host specified by `MHS_SDS_REDIS_CACHE_HOST`. Defaults to `6379`.
* `MHS_SDS_REDIS_DISABLE_TLS` (Spine Route Lookup service only) An optional flag that can be set to disable TLS for
connections to the Redis cache used by the Spine Route Lookup service. *Must* be set to exactly `True` for TLS to be
disabled.

Note that if you are using Opentest, you should use the credentials you were given when you got access to set `MHS_SECRET_PARTY_KEY`, `MHS_SECRET_CLIENT_CERT`, `MHS_SECRET_CLIENT_KEY` and `MHS_SECRET_CA_CERTS`.

## Running Unit Tests
- `pipenv run unittests` will run all unit tests.
- `pipenv run unittests-cov` will run all unit tests, generating a [Coverage](https://coverage.readthedocs.io/) report
in the `test-reports` directory.
- `pipenv run coverage-report` will print the coverage report generated by `unittests-cov`
- `pipenv run coverage-report-xml` will produce an XML version of the coverage report generated by `unittests-cov`, in a
[Cobertura](http://cobertura.github.io/cobertura/) compatible format
- `pipenv run coverage-report-html` will produce an HTML version of the coverage report generated by `unittests-cov`

## Coverage
`pipenv run unittests-cov` will run all unit tests with coverage enabled. \
`pipenv run coverage-report-xml` will generate an xml file which can then be submitted for coverage analysis.

## Analysis
To use sonarqube analysis you will need to have installed `sonar-scanner`. \
Ensure sonar-scanner is on your path, and configured for the sonarqube host with appropriate token.
 (See: [SonarQube](https://gpitbjss.atlassian.net/wiki/x/XQFfXQ))\
`sonar-scanner` will use `sonar-project.properties` to submit source to sonarqube for analysis. \
NOTE: Coverage will not show in the analysis unless you have already generated the xml report (as per above.)

## Running Integration Tests
`pipenv run inttests` will run all integration tests.

When running the tests locally, you will need to set the MHS_ADDRESS and ASID in the 'Environment variables' section of
 the Run/Debug Configurations.
- The ASID is a 12 digit number needed to access Opentest, supplied by NHS Digital
    - eg ASID=123456789012
- The MHS_ADDRESS is the hostname of the MHS instance being used for testing and should be supplied in it's raw state,
 without the 'http://' prefix or '/' suffix
    - eg MHS_ADDRESS=localhost will be resolved as 'http://localhost/'

Timeouts received whilst waiting for a response from Spine on a Windows machine could be due to the machine rejecting incoming connections on port 443. In order to open the port, follow these instructions:
https://docs.microsoft.com/en-us/windows/security/threat-protection/windows-firewall/create-an-inbound-port-rule

Any content POSTed to `/` on port 80 will result in the request configuration for the `path` entry in
`data/interactions.json` being loaded and the content sent as the body of the request to Spine. Adding entries to
`interactions.json` will allow you to define new supported interactions.
