----=_MIME-Boundary
Content-Id: <ebXMLHeader@spine.nhs.uk>
Content-Type: text/xml; charset=UTF-8
Content-Transfer-Encoding: 8bit

<?xml version="1.0" encoding="UTF-8"?>
<SOAP:Envelope xmlns:xsi="http://www.w3c.org/2001/XML-Schema-Instance" xmlns:SOAP="http://schemas.xmlsoap.org/soap/envelope/" xmlns:eb="http://www.oasis-open.org/committees/ebxml-msg/schema/msg-header-2_0.xsd" xmlns:hl7ebxml="urn:hl7-org:transport/ebXML/DSTUv1.0" xmlns:xlink="http://www.w3.org/1999/xlink">
<SOAP:Header>
	<eb:MessageHeader SOAP:mustUnderstand="1" eb:version="2.0">
		<eb:From>
			<eb:PartyId eb:type="urn:nhs:names:partyType:ocs+serviceInstance">YES-0000806</eb:PartyId>
		</eb:From>
		<eb:To>
			<eb:PartyId eb:type="urn:nhs:names:partyType:ocs+serviceInstance">FROM_PARTY_ID</eb:PartyId>
		</eb:To>
		<eb:CPAId>S1001A1630</eb:CPAId>
		<eb:ConversationId>10F5A436-1913-43F0-9F18-95EA0E43E61A</eb:ConversationId>
		<eb:Service>urn:nhs:names:services:psis</eb:Service>
		<eb:Action>MCCI_IN010000UK13</eb:Action>
		<eb:MessageData>
			<eb:MessageId>C614484E-4B10-499A-9ACD-5D645CFACF61</eb:MessageId>
			<eb:Timestamp>2019-05-04T20:55:16Z</eb:Timestamp>
		</eb:MessageData>
        <eb:DuplicateElimination/>
    </eb:MessageHeader>
    <eb:AckRequested SOAP:mustUnderstand="1" eb:version="2.0" eb:signed="false" SOAP:actor="urn:oasis:names:tc:ebxml-msg:actor:toPartyMSH"/>
    <eb:SyncReply SOAP:mustUnderstand="1" eb:version="2.0" SOAP:actor="http://schemas.xmlsoap.org/soap/actor/next"/>
</SOAP:Header>
<SOAP:Body>
	<eb:Manifest SOAP:mustUnderstand="1" eb:version="2.0">
		<eb:Reference xlink:href="cid:C614484E-4B10-499A-9ACD-5D645CFACF61@spine.nhs.uk">
			<eb:Schema eb:location="http://www.nhsia.nhs.uk/schemas/HL7-Message.xsd" eb:version="1.0"/>
			<eb:Description xml:lang="en">HL7 payload</eb:Description>
			<hl7ebxml:Payload style="HL7" encoding="XML" version="3.0"/>
		</eb:Reference>
	</eb:Manifest>
</SOAP:Body>
</SOAP:Envelope>

----=_MIME-Boundary
Content-Id: <C614484E-4B10-499A-9ACD-5D645CFACF61@spine.nhs.uk>
Content-Type: text/xml; charset=UTF-8
Content-Transfer-Encoding: 8bit

<hl7:MCCI_IN010000UK13 xmlns:hl7="urn:hl7-org:v3"/>
----=_MIME-Boundary--
