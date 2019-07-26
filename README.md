# National Integration Adaptor

This repository contains adaptors which accelerate integration with national NHS systems.

These adaptors hide the complexity of integration with the interfaces provided by the current national systems by
implementing an adaptor layer. The integrating supplier sees only a simplified and standardised set of interfaces which
the adaptor layer presents. The adaptor layer is responsible for interacting with the legacy NHSD interface estate. 

![High Level Architecture](documentation/High%20Level%20Architecture.png)

As a result, the complexity of integration work is much reduced. The integrating supplier is required to implement a
minimum set of client types in their interface layer and can re-use this code across multiple integrations.

## Repository Contents
This repository contains the following directories:
- [common](common) - A Python package containing components and utilities that are common to several integration adaptors.
- [documentation](documentation) - Documentation and assets for the integration adaptors as a whole.
- [mhs-reference-implementation](mhs-reference-implementation) - A reference implementation of a Message Handling
Service (MHS), that encapsulates the details of Spine messaging and provides a simple interface to allow HL7 messages to
be sent to the NHS spine MHS.
- [nhais-adaptor](nhais-adaptor) - A proof-of-concept adaptor that hides the details of NHAIS' EDIFACT messaging format
and provides a prototype FHIR interface for sending registratio events taking place at the practice to NHAIS.
- [OneOneOne](OneOneOne) - A proof-of-concept 111 receiver, also used to investigate use of the ITK testbench (the TKW).
- [pipeline](pipeline) - Scripts and configuration files used to build container images for adaptors and deploy them to various
environments. Intended for use as part of an automated build pipeline.
- [SCR](SCR) - A package of assets that simplify the building of HL7 GP Summary Update request messages.
- [supplier-example](supplier-example) - An example web application that uses the assets from the SCR package to
generate a GP Summary Update request and send it to an instance of the MHS reference implementation. Intended to show
how the adaptors can be used together to simplify integration.

Each directory contains its own README.md file which provides more details.
