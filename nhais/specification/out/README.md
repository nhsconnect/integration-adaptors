# Documentation for NHAIS Adaptor (FHIR) API

<a name="documentation-for-api-endpoints"></a>
## Documentation for API Endpoints

All URIs are relative to *https://localhost*

Class | Method | HTTP request | Description
------------ | ------------- | ------------- | -------------
*PatientsApi* | [**acceptPatient**](Apis/PatientsApi.md#acceptpatient) | **POST** /Patient/{id} | Accept a new patient (Acceptance transaction)
*PatientsApi* | [**deductPatient**](Apis/PatientsApi.md#deductpatient) | **POST** /Patient/{id}/$nhais.deduction | Deduct a patient (Deduction transaction)
*PatientsApi* | [**removePatient**](Apis/PatientsApi.md#removepatient) | **POST** /Patient/{id}/$nhais.removal | Accept a new patient (Acceptance transaction)
*PatientsApi* | [**updatePatientPartial**](Apis/PatientsApi.md#updatepatientpartial) | **PATCH** /Patient/{id} | Amend patient details (Amendment transaction)


<a name="documentation-for-models"></a>
## Documentation for Models

 - [Address](.//Models/Address.md)
 - [AddressKey](.//Models/AddressKey.md)
 - [ContactPoint](.//Models/ContactPoint.md)
 - [Deduction](.//Models/Deduction.md)
 - [DeductionExtension](.//Models/DeductionExtension.md)
 - [ErrorCode](.//Models/ErrorCode.md)
 - [ErrorCodeCoding](.//Models/ErrorCodeCoding.md)
 - [Gender](.//Models/Gender.md)
 - [GeneralPractitionerReference](.//Models/GeneralPractitionerReference.md)
 - [GeneralPractitionerReferenceIdentifier](.//Models/GeneralPractitionerReferenceIdentifier.md)
 - [HumanName](.//Models/HumanName.md)
 - [InlineObject](.//Models/InlineObject.md)
 - [Meta](.//Models/Meta.md)
 - [MetaSecurity](.//Models/MetaSecurity.md)
 - [NHSNumberVerificationStatus](.//Models/NHSNumberVerificationStatus.md)
 - [NHSNumberVerificationStatus2](.//Models/NHSNumberVerificationStatus2.md)
 - [NHSNumberVerificationStatus2Coding](.//Models/NHSNumberVerificationStatus2Coding.md)
 - [OperationIdentifier](.//Models/OperationIdentifier.md)
 - [OperationIdentifierExtension](.//Models/OperationIdentifierExtension.md)
 - [OperationOutcome](.//Models/OperationOutcome.md)
 - [OperationOutcomeIssue](.//Models/OperationOutcomeIssue.md)
 - [Patient](.//Models/Patient.md)
 - [Period](.//Models/Period.md)


<a name="documentation-for-authorization"></a>
## Documentation for Authorization

All endpoints do not require authorization.
