# MHS

This package contains a pre-assured implementation of a Message Handling System (MHS), intended to encapsulate the
details of Spine messaging and provide a simple interface to allow HL7 messages to be sent to a remote MHS.

## Setup
A `data/certs` directory should be created with the following files (containing the certificates & keys required to
perform client authentication to the Spine instance you are using. For Openttest, these will have been provided when you
were granted access):
- `client.cert` - Should include the following in this order: endpoint certificate, endpoint issuing subCA certificate,
root CA Certificate.
- `client.key` - Your endpoint private key
- `client.pem` - A copy of client.cert
- `party_key.txt` - The party key associated with your MHS build

If you are using Opentest, each of these credentials will have been provided when you were granted access.

Finally, ensure you have [Pipenv](https://docs.pipenv.org/en/latest/) installed and on your path, then from this
directory run:
```
pipenv install
```

### Developer Setup
To prepare a development environment for this application, ensure you have [Pipenv](https://docs.pipenv.org/en/latest/)
installed and on your path, then from this directory run:
```
pipenv install --dev
```

## Running Unit Tests
`pipenv run unittests` will run all unit tests.

## Running Integration Tests
`pipenv run inttests` will run all integration tests.

When running the tests locally, you will need to set the MHS_ADDRESS and ASID in the 'Environment variables' section of
 the Run/Debug Configurations.
- The ASID is a 12 digit number needed to access Opentest, supplied by NHS Digital
    - eg ASID=123456789012
- The MHS_ADDRESS is the hostname of the MHS instance being used for testing and should be supplied in it's raw state,
 without the 'http://' prefix or '/' suffix
    - eg MHS_ADDRESS=localhost will be resolved as 'http://localhost/'

## Running an MHS Instance
`pipenv run mhs` will run the `main.py` script (you can also run this directly). This will start up an MHS
instance listening for 'client' requests on port 80 and asynchronous responses from Spine on port 443.
Note that the following environment variables need to be set when running MHS:
- `MHS_LOG_LEVEL` - log level threshold

Any content POSTed to `/path` (for example) on port 80 will result in the request configuration for the `path` entry in
`data/interactions.json` being loaded and the content sent as the body of the request to Spine. Adding entries to
`interactions.json` will allow you to define new supported interactions.

You will need to complete the setup steps below before being able to successfully connect to a Spine instance.
