# Integration Tests

This package contains a the integration tests intended to pre-assure the Message Handling Service and all the
associated services/interfaces used in the Spine messaging.

## Running the Integration Tests
`pipenv run inttests` will run all integration tests.

When running the tests locally, you will need to set the MHS_ADDRESS and ASID in the 'Environment variables' section of
 the Run/Debug Configurations.
- The ASID is a 12 digit number needed to access Opentest, supplied by NHS Digital
    - eg ASID=123456789012
- The MHS_ADDRESS is the hostname of the MHS instance being used for testing and should be supplied in it's raw state,
 without the 'http://' prefix or '/' suffix
    - eg MHS_ADDRESS=localhost will be resolved as 'http://localhost/'


You will need to complete the setup steps for all the associated services in test prior to running this test suite
