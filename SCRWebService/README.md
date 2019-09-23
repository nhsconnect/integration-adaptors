# Summary Care Record Web Service
 This is a web service which provides a simple interface with which 
a supplier can perform Summary Care Record (SCR) based actions. A supplier will provide JSON formatted input data 
for a particular SCR function, this data will then be used to populate templates for SCR functions producing
 a HL7 message which is forwarded to an MHS and further to spine.
 
The SCR Web Service requires several environment variables to run:

* SCR_LOG_LEVEL: Level of logging 
* SCR_MHS_ADDRESS: The address of the MHS that the SCR adaptor will forward requests to
