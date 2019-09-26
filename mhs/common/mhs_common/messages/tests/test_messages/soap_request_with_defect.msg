<?xml version="1.0" encoding="utf-8"?>
<SOAP-ENV:Envelope xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/" xmlns:wsa="http://schemas.xmlsoap.org/ws/2004/08/addressing" xmlns:hl7="urn:hl7-org:v3">
	<SOAP-ENV:Header>
		<wsa:Action>urn:nhs:names:services:pdsquery/QUPA_IN040000UK32</wsa:Action>
		<wsa:To>https://pds-sync.national.ncrs.nhs.uk/syncservice-pds/pds</wsa:To>
		<wsa:From>
			<wsa:Address/>
		</wsa:From>
		<hl7:communicationFunctionRcv>
			<hl7:device>
                <hl7:id xmlns:SOAP="http://schemas.xmlsoap.org/soap/envelope/" extension="000009199092" root="1.2.826.0.1285.0.2.0.107"/>
			</hl7:device>
		</hl7:communicationFunctionRcv>
		<hl7:communicationFunctionSnd>
			<hl7:device>
                <hl7:id xmlns:SOAP="http://schemas.xmlsoap.org/soap/envelope/" extension="918999199111" root="1.2.826.0.1285.0.2.0.107"/>
			</hl7:device>
		</hl7:communicationFunctionSnd>
		<wsa:ReplyTo>
			<wsa:Address/>
		</wsa:ReplyTo>
	</SOAP-ENV:Header>
	<SOAP-ENV:Body>
		<QUPA_IN040000UK32 xmlns="urn:hl7-org:v3" xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/" xmlns:wsa="http://schemas.xmlsoap.org/ws/2004/08/addressing" xmlns:hl7="urn:hl7-org:v3">text</QUPA_IN040000UK32>
    </SOAP-ENV:Body>
</SOAP-ENV:Envelope>
