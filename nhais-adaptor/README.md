# NHAIS Adaptor

An adaptor for interfacing with NHAIS.

## Outgoing
Will take a FHIR payload and convert to an EDIFACT message to be consumed by NHAIS

## Incoming
Will take an EDIFACT message and convert to a FHIR response to be consumed by the GP system

## Installation
Ensure you have `pipenv` installed and is on your class path

### Run the tests
`pipenv run tests` to run all the tests

### Test the adaptor
`pipenv run transfer` - Loads the fhir patient registration payload in the GP outbox. 
Runs the adaptor and creates the edifact interchange in the NHAIS inbox
