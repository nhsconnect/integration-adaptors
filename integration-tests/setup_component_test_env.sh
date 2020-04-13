#!/bin/bash

set -e

mkdir -p ./generated-certs/fake-spine/
mkdir -p ./generated-certs/inbound/
mkdir -p ./generated-certs/outbound/

(cd ./generated-certs/fake-spine || exit; openssl req -x509 -subj "/CN=fakespine" -newkey rsa:2048 -nodes -keyout key.pem -out cert.pem -days 365)
(cd ./generated-certs/inbound || exit; openssl req -x509 -subj "/CN=inbound" -newkey rsa:2048 -nodes -keyout key.pem -out cert.pem -days 365)
(cd ./generated-certs/outbound || exit; openssl req -x509 -subj "/CN=outbound" -newkey rsa:2048 -nodes -keyout key.pem -out cert.pem -days 365)

touch component-test-source.sh
echo -e "export FAKE_SPINE_CERTIFICATE=\"$(cat ./generated-certs/fake-spine/cert.pem)\"" >> component-test-source.sh
echo -e "export FAKE_SPINE_PRIVATE_KEY=\"$(cat ./generated-certs/fake-spine/key.pem)\"" >> component-test-source.sh
echo -e "export OUTBOUND_CERTIFICATE=\"$(cat ./generated-certs/outbound/cert.pem)\"" >> component-test-source.sh
echo -e "export OUTBOUND_PRIVATE_KEY=\"$(cat ./generated-certs/outbound/key.pem)\"" >> component-test-source.sh
echo -e "export INBOUND_CERTIFICATE=\"$(cat ./generated-certs/inbound/cert.pem)\"" >> component-test-source.sh
echo -e "export INBOUND_PRIVATE_KEY=\"$(cat ./generated-certs/inbound/key.pem)\"" >> component-test-source.sh
echo -e "export FAKE_SPINE_CA_STORE=\"$(cat ./generated-certs/outbound/cert.pem)\n$(cat ./generated-certs/inbound/cert.pem)\"" >> component-test-source.sh
echo -e "export OUTBOUND_CA_STORE=\"$(cat ./generated-certs/fake-spine/cert.pem)\"" >> component-test-source.sh
echo -e "export INBOUND_CA_STORE=\"$(cat ./generated-certs/fake-spine/cert.pem)\"" >> component-test-source.sh
echo -e "export MHS_SECRET_PARTY_KEY=\"test-party-key\"" >> component-test-source.sh
echo -e "export MHS_OUTBOUND_VALIDATE_CERTIFICATE=\"False\"" >> component-test-source.sh
rm -rf ./generated-certs