<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:SOAP="http://schemas.xmlsoap.org/soap/envelope/"
        xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/">
<xsl:output method="xml" omit-xml-declaration="yes" indent="no" />

	<xsl:template match="/">
        <xsl:copy-of select="//SOAP-ENV:Body/*" />
    </xsl:template>

</xsl:stylesheet>