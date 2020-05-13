#!/bin/bash

# gathers env values and secrets to one file, which then can be souced by main script

# env vars

echo "export INBOUND_SERVER_BASE_URL=http://${INBOUND_SERVER_BASE_URL}:443" > /var/variables_source.sh
echo "export FAKE_SPINE_OUTBOUND_DELAY_MS=${FAKE_SPINE_OUTBOUND_DELAY_MS}" >> /var/variables_source.sh
echo "export FAKE_SPINE_INBOUND_DELAY_MS=${FAKE_SPINE_INBOUND_DELAY_MS}" >> /var/variables_source.sh
echo "export FAKE_SPINE_OUTBOUND_SSL_ENABLED=${FAKE_SPINE_OUTBOUND_SSL_ENABLED}" >> /var/variables_source.sh
echo "export FAKE_SPINE_PORT=${FAKE_SPINE_PORT}" >> /var/variables_source.sh
echo "export FAKE_SPINE_PROXY_VALIDATE_CERT=${FAKE_SPINE_PROXY_VALIDATE_CERT}" >> /var/variables_source.sh
echo "export MHS_LOG_LEVEL=${MHS_LOG_LEVEL}" >> /var/variables_source.sh

# secret vars
echo "export FAKE_SPINE_PRIVATE_KEY=\"$(aws secretsmanager get-secret-value --region ${REGION} --secret-id ${FAKE_SPINE_PRIVATE_KEY_ARN} --query SecretString --output text)\"" >> /var/variables_source.sh
echo "export FAKE_SPINE_CERTIFICATE=\"$(aws secretsmanager get-secret-value --region ${REGION} --secret-id ${FAKE_SPINE_CERTIFICATE_ARN} --query SecretString --output text)\"" >> /var/variables_source.sh
echo "export FAKE_SPINE_CA_STORE=\"$(aws secretsmanager get-secret-value --region ${REGION} --secret-id ${FAKE_SPINE_CA_STORE_ARN} --query SecretString --output text)\"" >> /var/variables_source.sh
echo "export MHS_SECRET_PARTY_KEY=$(aws secretsmanager get-secret-value --region ${REGION} --secret-id ${MHS_SECRET_PARTY_KEY_ARN} --query SecretString --output text)" >> /var/variables_source.sh
