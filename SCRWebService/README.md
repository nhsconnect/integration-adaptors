#Summary Care Record Web Service
 This is a web service which provides a simple interface with which 
a supplier can perform Summary Care Record (SCR) based actions. A supplier will provide JSON formatted input data 
for a particular SCR function, this data will then be used to populate templates for SCR functions producing
 a HL7 message which is forwarded to an MHS and further to spine.
 
 A simple integration test is provided, by default the application runs on port 9000 but this can be set 
 with the environment variable `SCR_SERVICE_PORT`, the integration test defaults to `http://localhost:9000`
 but again this can be changed with the environment variable `SCR_SERVICE_ADDRESS`.