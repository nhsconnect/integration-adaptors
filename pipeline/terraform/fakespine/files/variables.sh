#!/bin/bash

# gathers env values and secrets to one file, which then can be souced by main script

# env vars

echo "export INBOUND_SERVER_BASE_URL         = ${INBOUND_SERVER_BASE_URL}" > /var/variables_source.sh
echo "export FAKE_SPINE_OUTBOUND_DELAY_MS    = ${FAKE_SPINE_OUTBOUND_DELAY_MS}" >> /var/variables_source.sh
echo "export FAKE_SPINE_INBOUND_DELAY_MS     = ${FAKE_SPINE_INBOUND_DELAY_MS}" >> /var/variables_source.sh
echo "export FAKE_SPINE_OUTBOUND_SSL_ENABLED = ${FAKE_SPINE_OUTBOUND_SSL_ENABLED}" >> /var/variables_source.sh
echo "export FAKE_SPINE_PORT                 = ${FAKE_SPINE_PORT}" >> /var/variables_source.sh

# secret vars