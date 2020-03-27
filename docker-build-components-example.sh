#!/bin/bash
: '
Make a copy of this file and rename to docker-build-components.sh
as the renamed file is in .gitignore. This will avoid commiting the file
with certificate information.
'
echo "Exporting environment variables"
#Put your party key here (OpenTest):
export MHS_SECRET_PARTY_KEY=""

#Put your endpoint certificate here (OpenTest):
MHS_SECRET_CLIENT_CERT=""

#Put your endpoint private key here (OpenTest):
MHS_SECRET_CLIENT_KEY=""

#Put your Endpoint issuing subCA certificate and your Root CA certificate here (OpenTest)
MHS_SECRET_CA_CERTS=""

#Stops containers, builds images and starts containers
echo "Stopping running containers"
docker-compose -f docker-compose.yml -f docker-compose.lb.override.yml stop;

echo "Build and starting containers"
docker-compose -f docker-compose.yml -f docker-compose.lb.override.yml up -d --build