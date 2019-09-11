<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:hl7="urn:hl7-org:v3"
                xmlns:wsa="http://schemas.xmlsoap.org/ws/2004/08/addressing">
<xsl:output method="xml" omit-xml-declaration="yes" indent="no" />

	<xsl:template match="/*">
        {
            "message_id": "<xsl:value-of select="//wsa:MessageID" />",
            "to_asid": "<xsl:value-of select="//hl7:communicationFunctionRcv/hl7:device/hl7:id/@extension" />",
            "from_asid": "<xsl:value-of select="//hl7:communicationFunctionSnd/hl7:device/hl7:id/@extension" />",
            "service": "<xsl:value-of select="//wsa:To" />",
            "action": "<xsl:value-of select="//wsa:Action" />"
        }
    </xsl:template>

</xsl:stylesheet>