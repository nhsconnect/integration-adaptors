# DeathNotificationStatus2Coding
## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**system** | [**String**](string.md) | URI of the coding system specification. | [default to null]
**version** | [**String**](string.md) | Version of the coding system in use. | [optional] [default to null]
**code** | [**String**](string.md) | Symbol, in syntax, defined by the system: * Code 1 - Informal death notice received via an update from a local NHS Organisation such as GP practice or Trust * Code 2 - Formal death notice received from Registrar of Deaths. Only these endpoints are allowed to add a Formal death:     - National Back Office using the Demographic Spine Application (DSA)     - Office of National Statistics (ONS)     - Maternity sites * Code U - Removed. This is a possible response, but it cannot be used on an update because Spine will reject it  | [default to null]
**display** | [**String**](string.md) | Representation defined by the system. | [optional] [default to null]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)

