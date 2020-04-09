# Meta
## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**versionId** | [**String**](string.md) | The NHS Digital assigned version of the patient resource. | [optional] [default to null]
**security** | [**List**](Meta_security.md) | The level of security on the patients record, which affects which fields are populated on retrieval. The possible responses are: * U - unrestricted. All available data will be returned. * R - restricted. Any sensitive data around the patients location, so &#x60;address&#x60;, &#x60;generalPractitioner&#x60; and &#x60;telecom&#x60;, will be removed from the response. Additionally, the death notification extension will be removed. * V - very restricted. All patient data will be removed from the response apart from &#x60;id&#x60;, &#x60;identifier&#x60; and &#x60;meta&#x60; fields. * REDACTED - redacted. The patient record has been marked as invalid, so the data should not be used. This code will never be returned; you will receive a 404, and appropriate error response, if an invalidated patient retrieval is attempted. It is also possible that no security field will be added to the response, which is the equivalent of unrestricted.  | [optional] [default to null]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)

