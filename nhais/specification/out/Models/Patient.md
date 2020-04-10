# Patient
## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**resourceType** | [**String**](string.md) | FHIR resource type. | [optional] [default to Patient]
**id** | [**String**](string.md) | The patient&#39;s NHS Number. The primary identifier of a patient, unique within NHS England and Wales. Always 10 digits and must be a [valid NHS Number](https://www.datadictionary.nhs.uk/data_dictionary/attributes/n/nhs/nhs_number_de.asp). | [optional] [default to null]
**identifier** | [**List**](object.md) | Identifier and system of identification used for this Patient. | [optional] [default to null]
**meta** | [**Meta**](Meta.md) |  | [optional] [default to null]
**name** | [**List**](HumanName.md) | List of names associated with the patient.  When a patient tagged as &#x60;very restricted&#x60; is retrieved, all names will be removed from the response.  | [default to null]
**gender** | [**Gender**](Gender.md) |  | [default to null]
**birthDate** | [**date**](date.md) | Date of birth. A date in the format &#x60;yyyy-mm-dd&#x60;.  When a patient tagged as &#x60;very restricted&#x60; is retrieved, birth date will be removed from the response.  | [default to null]
**deceasedDateTime** | [**Date**](DateTime.md) | Date and time of death, if applicable and known. A datetime in the format &#x60;yyyy-mm-ddTHH:MM:SS+HH:MM&#x60;.  When a patient tagged as &#x60;very restricted&#x60; is retrieved, death date will be removed from the response.  | [optional] [default to null]
**address** | [**List**](Address.md) | List of addresses associated with the patient.  This will only be fully populated on a retrieval, only a the &#x60;home&#x60; address will be returned on a search.  When a patient tagged as &#x60;restricted&#x60; or &#x60;very restricted&#x60; is retrieved, all addresses will be removed from the response.  | [default to null]
**telecom** | [**List**](ContactPoint.md) | List of contact points for the patient; for example, phone numbers or email addresses.  When a patient tagged as &#x60;restricted&#x60; or &#x60;very restricted&#x60; is retrieved, all contact points will be removed from the response.  | [optional] [default to null]
**generalPractitioner** | [**List**](GeneralPractitionerReference.md) | General Practice (not practitioner) with which the patient is, or was, registered. Always contains zero or one general practitioner object.  When a patient tagged as &#x60;restricted&#x60; or &#x60;very restricted&#x60; is retrieved, the General Practice will be removed from the response.  | [optional] [default to null]
**extension** | [**List**](anyOf&lt;Deduction&gt;.md) |  | [optional] [default to null]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)

