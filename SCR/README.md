#### **Proof of Concept: Summary Care Record**

The objective of this PoC was to provide a set of assets that would assist a new supplier in the implementation of the Gp Summary Update action[1] of the spine system. 

Within the GpSummaryUpdate schema there exists a large amount of fixed data which does not vary between messages. This library reduces the workload required to generate a GpSummaryUpload message by identifying the parts of the message which are actually variable (such as supplier IDs, author information, and human readable updates) and templating them so a supplier only has to concern themselves with the variable data which can be populated with a json object.

Within the `data/templates` directory there exists a `mustache` [2] template[3] of the message to be sent to the spine system, and in the `scr/gpsummaryupdate` module there is a simple interface for populating the template. This interface can take either a python dictionary or a json file path which will contain the values for the variable portions of the template. The interface will return the template populated with the values of the dictionary as an xml string.

Examples of the usage of the interface can be found in the `scr/tests/test_gpsummaryupdate` module and examples of the 
json/dictionaries consumed by the interface can be seen in the `scr/tests/hashes` folder.

The output from this interface can be injected into the OpenTest module which allows us to demonstrate how the output from this package would be used with a SOAP wrapper to be sent to Spine. The output from this package could also be passed to the MHS PoC to be sent to spine upon completion of the MHS PoC.

[1] - Gp Summary Update schema action defined in the MIM: https://data.developer.nhs.uk/dms/mim/4.2.00/Domains/GP%20Summary/Document%20files/GP%20Summary%20IM.htm#_Toc_Section_7.2

[2] - Mustache templating: https://mustache.github.io/

[3] - The main template is 16UK05.mustache, this `templates` directory also contains additional templates which are partials, these are imported to the main template to simplifiy the main template
