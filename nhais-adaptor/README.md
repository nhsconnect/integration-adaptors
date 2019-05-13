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

- `pipenv run outgoing`
Select the GP outbox and fhir payload file. An edifact interchange file will be
generated in the NHAIS inbox. 

- `pipenv run incoming`
Select the NHAIS outbox and edifact file. Depending on the edifact interchange multiple fhir payloads will be generated
in the GP's inbox. 
