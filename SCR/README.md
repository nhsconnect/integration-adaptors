#### **Summary Care Record**

This package provides assets to assist suppliers in the implementation of the Summary Care Record(SCR) actions, the
focus in this package was on the GP Summary Upload action[1] . Within the GP Summary Update XML schema there exists 
a large amount of fixed data which does not vary between messages. This library reduces the workload required 
to generate a GP Summary Upload message by identifying the parts of the message which are actually
 variable (such as supplier IDs, author information, and human readable updates) and templating them so a 
 supplier only has to concern themselves with the variable data which can be populated with a json object.

Within the `data/templates` directory there exists a `mustache`[2] template[3] of the message to be sent to the Spine 
system, and in the `scr/gpsummaryupdate` module there is a simple interface for populating the template. 
This interface can take either a python dictionary or a json file path which will contain the values for the 
variable portions of the template. The interface will return the template populated with the values of the 
dictionary as an xml string.

The `scr/gpsummaryupdate` module also provides an interface for parsing an acknowledgement of a successful 
GP summary upload from spine (the async response). Note that this is just the successful response message, error
response parsing is not supported at the current time.

Examples of the usage of the interface can be found in the `scr/tests/test_gpsummaryupdate` module and examples of the 
json/dictionaries consumed by the interface can be seen in the `scr/tests/hashes` folder.

This library has been used as part of the `integration-adaptors/SCRWebService` project to provide the templating
for the GP summary upload messages before being forwarded to the MHS and further onto Spine.

Finally it should be noted that this package does not support population of structured information within the
GP summary upload message (this is the content within the `pertinentInfomation2` tags in the message), the tags have
been included to comply with the message schema but contain no contents, should this ever be extended the template
for the tags can be found in `data/templates/pertinentInformation2Partial.mustache`.


[1] - Gp Summary Update schema action defined in the MIM: 
https://data.developer.nhs.uk/dms/mim/4.2.00/Domains/GP%20Summary/Document%20files/GP%20Summary%20IM.htm#_Toc_Section_7.2

[2] - Mustache templating: https://mustache.github.io/

[3] - The main template is 16UK05.mustache, this `templates` directory also contains additional templates which are
 partials, these are imported to the main template to simplify the main template
