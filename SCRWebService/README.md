# Summary Care Record Web Service
 This is a web service which provides a simple interface with which 
a supplier can perform Summary Care Record (SCR) based actions. A supplier will provide JSON formatted input data 
for a particular SCR function, this data will then be used to populate templates for SCR functions producing
 a HL7 message which is forwarded to an MHS and further to spine.
 
The SCR Web Service requires several environment variables to run:

* SCR_LOG_LEVEL: Level of logging 
* SCR_MHS_ADDRESS: The address of the MHS that the SCR adaptor will forward requests to


The SCR Web Service uses the SCR package to populate and parse GP Summary Upload messages, the parsed response 
(and the response returned to the supplier on success) contains the following values:

- messageId: The Id of the asynchronous response from spine acknowledging successful execution of the Gp Summary 
upload
- messageRef: The message Id associated with outbound message (relative to the MHS) containing the 
actual Gp Summary Upload payload, this is the Id of the message received by spine.
- creationTime: The time the async response message was created, in yyyymmddhhmmss time format
- messageDetail: The contents of the messageDetail tag of the response, usually contains details of the 
success response such as `GP Summary upload successful`  


Examples of the usage and interface of the SCR can be found within the integration tests directory, details are 
provided below:

#####Headers:

- interaction-name (required): The name of the particular interaction to send to the MHS, this is a human readable name that 
maps internally in the SCR Adaptor to interaction-ids, current support mappings are:
    - `SCR_GP_SUMMARY_UPLOAD` -> `REPC_IN150016UK05`
- correlation-id: A logging Id used to track messages through the SCR Adaptor and the MHS for debugging, this will
be generated internally if not provided 
- message-id: The outbound message id associated with the message to be sent to Spine, this ID will be generated
by the MHS

#####Body
The message body is a json object containing the values used to populate the xml template, this message body must
contain all keys even if the values are empty. Examples of message bodies can be found within the unit tests and 
another example is provided in `integration-adaptors/integration-tests/data/templates/json_16UK05.mustache`
