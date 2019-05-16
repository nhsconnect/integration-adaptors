
####__**111 Receiver Proof of Concept**__

This module includes a basic example of a 111 receiver implemented to help identify the complexities
of implementing a 111 receiver and analyse the effectiveness of the ITK testbench (the TKW) as a development aid. As
a mock receiver the roll of this end point is to receive messages from a 111 Post Event Message (PEM) sender, 
validate the message against the specification outlined in the ITK conformance document and respond to the sender
appropriately.

####**Usage**
This module can be cloned and the requirements installed using pipenv, the tests can be run using:
`pipenv run tests` and the main web service environment can be run via pycharm. Running the `web_service.py` module will
start an end point capable of receiving 111 messages and performing basic validation for the following specification
conditions:

* _DIST_BadService_: Bad distribution envelope, service not matching SOAP action
* _DIST_BadManifestPayloadCounts_: Manifest count not equalling payload count
* _DIST_BadManifestCount_: The number of manifest instances does not equal the count specified
* _DIST_BadPayloadIDManifestID_: Payload ID not equal to the Manifest ID
* _BadPayloadCount_[1]: Number of payload instances does not equal the count specified 
 

Additionally the majority of the 'success' test conditions provided by the TKW will pass when run against this end point, though no 
specific validation for their conditions is performed, simply a mock success message is returned.


####*The ITK Test Bench*
This tool was built to be used with the ITK TestBench - the TKW[2]. The TKW comes with a range of documentation
and videos demonstrating installation and setup. Once installed specify the endpoint location in the Autotest manager
configuration tab (by default this endpoint runs on port 4848), navigate to the `Run Tests` tab and select the `NHS 111`
domain in the drop down, then select the `Gp Receiver Testcases` from the selected bundles. You will then see a list
of supported tests in the TKW to test a 111 receiver end point. From here you will be able to select the specified tests
you wish to run, the ones described above will pass against this code library.


####*Limitations*
The end point here provides a limited subset of the test cases required by the 111 receiver specification. There is
also a known issue where the TKW will return unpredictable failed tests cases due to a null HTTP response, this issue
has been tested across different languages and frameworks. This issue was followed up with the ITK helpdesk and 
unfortunately a solution was not found, it is unclear if this is an issue with this end point or the TKW. 

[1] - This is not a supported test condition in the TKW, but is part of the specification
[2] - The TKW can be downloaded here: https://developer.nhs.uk/testcentre/itk-testbench/