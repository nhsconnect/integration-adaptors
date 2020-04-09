# PatientsApi

All URIs are relative to *https://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**acceptPatient**](PatientsApi.md#acceptPatient) | **POST** /Patient/{id} | Accept a new patient (Acceptance transaction)
[**deductPatient**](PatientsApi.md#deductPatient) | **POST** /Patient/{id}/$nhais.deduction | Deduct a patient (Deduction transaction)
[**removePatient**](PatientsApi.md#removePatient) | **POST** /Patient/{id}/$nhais.removal | Accept a new patient (Acceptance transaction)
[**updatePatientPartial**](PatientsApi.md#updatePatientPartial) | **PATCH** /Patient/{id} | Amend patient details (Amendment transaction)


<a name="acceptPatient"></a>
# **acceptPatient**
> OperationOutcome acceptPatient(id, patient)

Accept a new patient (Acceptance transaction)

    ## Overview Use this endpoint to send an Acceptance to NHAIS.  ## Operation Id When you submit an amendment an operation id will be included in the response. This operation id MUST be retained to match against the asynchronous reply from NHAIS  ## Sandbox test scenarios TODO: document interactions supported by fake mesh  | Scenario                            | Request                                                      | Response                                         | | ----------------------------------- | ------------------------------------------------------------ | ------------------------------------------------ | |                                     |                                                              |                                                  | 

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **String**| The patient&#39;s NHS Number. The primary identifier of a patient, unique within NHS England and Wales. Always 10 digits and must be a [valid NHS Number](https://www.datadictionary.nhs.uk/data_dictionary/attributes/n/nhs/nhs_number_de.asp). | [default to null]
 **patient** | [**Patient**](..//Models/Patient.md)|  |

### Return type

[**OperationOutcome**](..//Models/OperationOutcome.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/fhir+json

<a name="deductPatient"></a>
# **deductPatient**
> OperationOutcome deductPatient(id, patient)

Deduct a patient (Deduction transaction)

    ## Overview Use this endpoint to send a Deduction transaction to NHAIS.  ## Operation Id When you submit an amendment an operation id will be included in the response. This operation id MUST be retained         to match against the asynchronous reply from NHAIS  ## EDIFACT  The following Interchange contains just one Deduction Request transaction for:  NHS Number N/10/10. Deduction Date : 25/12/1991, Deduction Reason : Death, Free Text : Died on holiday in Majorca. Registered with GP 281 (GMC National GP Code 4826940).  Information transmitted within Interchange 2, Message 3, Transaction Number 17 at 13:17 on 13/01/1992.  UNB+UNOA:2+TES5+XX11+920113:1317+00000002&#39; UNH+00000003+FHSREG:0:1:FH:FHS001&#39; BGM+++507&#39; NAD+FHS+XX1:954&#39; DTM+137:199201131317:203&#39; RFF+950:G5&#39; S01+1&#39; RFF+TN:17&#39; NAD+GP+4826940,281:900&#39; GIS+1:ZZZ&#39; DTM+961:19911225:102&#39; FTX+RGI+++DIED ON HOLIDAY IN MAJORCA&#39; S02+2&#39; PNA+PAT+N/10/10:OPI&#39; UNT+14+00000003&#39; UNZ+1+00000002&#39;   ## Sandbox test scenarios TODO: document interactions supported by fake mesh  | Scenario                            | Request                                                      | Response                                         | | ----------------------------------- | ------------------------------------------------------------ | ------------------------------------------------ | |                                     |                                                              |                                                  | 

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **String**| The patient&#39;s NHS Number. The primary identifier of a patient, unique within NHS England and Wales. Always 10 digits and must be a [valid NHS Number](https://www.datadictionary.nhs.uk/data_dictionary/attributes/n/nhs/nhs_number_de.asp). | [default to null]
 **patient** | [**Patient**](..//Models/Patient.md)|  |

### Return type

[**OperationOutcome**](..//Models/OperationOutcome.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/fhir+json

<a name="removePatient"></a>
# **removePatient**
> OperationOutcome removePatient(id, patient)

Accept a new patient (Acceptance transaction)

    ## Overview Use this endpoint to send a Removal transaction to NHAIS.  ## Operation Id TODO: operation id (transaction id) will probably need to be provided in the request since this is a reply to a HA -&gt; GP amendment  ## Sandbox test scenarios TODO: document interactions supported by fake mesh  | Scenario                            | Request                                                      | Response                                         | | ----------------------------------- | ------------------------------------------------------------ | ------------------------------------------------ | |                                     |                                                              |                                                  | 

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **String**| The patient&#39;s NHS Number. The primary identifier of a patient, unique within NHS England and Wales. Always 10 digits and must be a [valid NHS Number](https://www.datadictionary.nhs.uk/data_dictionary/attributes/n/nhs/nhs_number_de.asp). | [default to null]
 **patient** | [**Patient**](..//Models/Patient.md)|  |

### Return type

[**OperationOutcome**](..//Models/OperationOutcome.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/fhir+json

<a name="updatePatientPartial"></a>
# **updatePatientPartial**
> OperationOutcome updatePatientPartial(id, inlineObject)

Amend patient details (Amendment transaction)

    ## Overview Use this endpoint to send an Amendment to NHAIS.  This is a &#39;patch&#39; operation, meaning you can update specific parts of the patient record (such as a name or an address), as opposed to having to update the entire record.  ## Operation Id When you submit an amendment an operation id will be included in the response. This operation id MUST be retained to match against the asynchronous reply from NHAIS  ## Sandbox test scenarios TODO: document interactions supported by fake mesh  | Scenario                            | Request                                                      | Response                                         | | ----------------------------------- | ------------------------------------------------------------ | ------------------------------------------------ | |                                     |                                                              |                                                  | 

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **String**| The patient&#39;s NHS Number. The primary identifier of a patient, unique within NHS England and Wales. Always 10 digits and must be a [valid NHS Number](https://www.datadictionary.nhs.uk/data_dictionary/attributes/n/nhs/nhs_number_de.asp). | [default to null]
 **inlineObject** | [**InlineObject**](..//Models/InlineObject.md)|  |

### Return type

[**OperationOutcome**](..//Models/OperationOutcome.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/fhir+json

