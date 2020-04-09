# HumanName
## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | [**String**](string.md) | Unique object identifier for this name. | [default to null]
**use** | [**String**](string.md) | How this name should be used. * usual - Known as, conventional or the one patient normally uses. A patient will always have a usual name. * temp - An alias or temporary name. This may also be used for temporary names assigned at birth or in emergency situations. * nickname - A name that the patient prefers to be addressed by, but is not part of their usual name. * old - This name is no longer in use (or was never correct, but retained for records). * maiden - Name changed for Marriage. A name used prior to changing name because of marriage. This term is not gender specific. The use of this term does not imply any particular history for a person&#39;s name.  The following use codes are included in the [name-use](https://www.hl7.org/fhir/valueset-name-use.html) value set, but should not be used and will not be returned as part of a retrieval. * official - The formal name as registered in an official (government) registry, but which name might not be commonly used. May be called \&quot;legal name\&quot;. * anonymous - Anonymous assigned name, alias, or pseudonym (used to protect a person&#39;s identity for privacy reasons).  | [default to null]
**period** | [**Period**](Period.md) |  | [optional] [default to null]
**given** | [**List**](string.md) | Given names, including any middle names. | [optional] [default to null]
**family** | [**String**](string.md) | Family name (often called Surname). | [default to null]
**prefix** | [**List**](string.md) | Name prefixes, titles, and prenominals. | [optional] [default to null]
**suffix** | [**List**](string.md) | Name suffices and postnominals. | [optional] [default to null]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)

