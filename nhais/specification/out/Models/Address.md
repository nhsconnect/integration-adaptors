# Address
## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | [**String**](string.md) | Unique system identifier for this address. | [default to null]
**period** | [**Period**](Period.md) |  | [optional] [default to null]
**use** | [**String**](string.md) | Purpose of this address: * home - a communication address at a home. * work - an office address. First choice for business related contacts during business hours. * temp - a temporary address. The period can provide more detailed information. * billing - a corresponding address nominated by the patient where communication can be sent.  | [default to null]
**line** | [**List**](string.md) | All lines of the address except the postal code. | [optional] [default to null]
**postalCode** | [**String**](string.md) | Postal code of the address. | [optional] [default to null]
**extension** | [**List**](AddressKey.md) | Postal Address File (PAF) key associated with this address formatted as a FHIR extension. Empty if no PAF key for the address is known, or an object specifying the code system of the address key and the value of the address key. | [optional] [default to null]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)

