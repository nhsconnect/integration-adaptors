# MHS Reference Implementation

This package contains a reference implementation of an MHS.

## Installation
To use this package as part of your project, ensure you have `pipenv` installed and on your path, then from your
project's directory run:
```
pipenv install
```

### Run Tests
`pipenv run tests` will run all tests.

### Send a Message
`pipenv run sender` will run the `main.py` script which will send an example GP Summary Upload message to Opentest.

A /certs directory is required with the following files (containing the certificates & keys provided when you registered
for Opentest):
- client.cert - Should include the following in this order: endpoint certificate, Endpoint issuing subCA certificate, Root CA Certificate, as provided by the Opentest team
- client.key - Your endpoint private key, as provided by the Opentest team
- client.pem - A copy of client.cert
