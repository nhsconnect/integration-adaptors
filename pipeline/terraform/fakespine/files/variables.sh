#!/bin/bash

# gathers env values and secrets to one file, which then can be souced by main script

# env vars

echo "export INBOUND_SERVER_BASE_URL         = ${INBOUND_SERVER_BASE_URL}" > /var/variables_source.sh
echo "export FAKE_SPINE_OUTBOUND_DELAY_MS    = ${FAKE_SPINE_OUTBOUND_DELAY_MS}" >> /var/variables_source.sh
echo "export FAKE_SPINE_INBOUND_DELAY_MS     = ${FAKE_SPINE_INBOUND_DELAY_MS}" >> /var/variables_source.sh
echo "export FAKE_SPINE_OUTBOUND_SSL_ENABLED = ${FAKE_SPINE_OUTBOUND_SSL_ENABLED}" >> /var/variables_source.sh
echo "export FAKE_SPINE_PORT                 = ${FAKE_SPINE_PORT}" >> /var/variables_source.sh

# secret vars

    # FAKE_SPINE_PRIVATE_KEY_ARN = var.fake_spine_private_key
    # FAKE_SPINE_CERTIFICAT_ARN  = var.fake_spine_certificate
    # FAKE_SPINE_CA_STORE_ARN    = var.fake_spine_ca_store
    # MHS_SECRET_PARTY_KEY_ARN   = var.party_key_arn

# FAKE_SPINE_PRIVATE_KEY = `aws secretsmanager get-secret-value --secret-id ${FAKE_SPINE_PRIVATE_KEY_ARN} --output text`