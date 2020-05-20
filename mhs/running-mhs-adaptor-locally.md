# Running the MHS and SCR adaptors locally

It may be useful to run these adaptors in a local environment. The following is a step-by-step guide on how to set this up.

* Pre-requisite: [Set up NHS Digital OpenTest connection](../setup-opentest.md)
* Requirements: 
    - Docker - for example [Docker for Windows](https://docs.docker.com/docker-for-windows/)
    - [Packer](https://www.packer.io/)
    - [Python 3](https://www.python.org/downloads/)
    - [Pipenv](https://pipenv.kennethreitz.org/en/latest/install/#pragmatic-installation-of-pipenv)
    - git bash (to run .sh files below)
* Set up Environment variable:
`export BUILD_TAG='latest'`
* Run the `./build.sh` script found in the top level directory of this project. This will build the following docker containers which 
are required to run the MHS Adaptor locally. 
    - Inbound service (An HTTP endpoint which spine communicates request back to you on)
    - Outbound service (An HTTP endpoint which you submit requests for spine on)
    - Routing service (An HTTP endpoint which the Outbound service uses internally to get routing and reliability information from spine)
    - SCR Adaptor (An HTTP endpoint which can be used to simplify Summary Care Record interactions, and call the MHS adaptor for you)
    
 * Set up Environment variables. The environment variables `MHS_SECRET_PARTY_KEY`, `MHS_SECRET_CLIENT_CERT`, `MHS_SECRET_CLIENT_KEY` and `MHS_SECRET_CA_CERTS` need to
  be set when running this command. These variables should be set as described [here](mhs-adaptor-dev-notes.md#environment-variables). 
  A simple way of setting this up once is to create a bash file `configure-env-vars.sh` that looks like:
  ```sh
  export MHS_SECRET_PARTY_KEY="your party key from NHS Digital here"
  export MHS_SECRET_CLIENT_CERT=$'client cert from NHS Digital here'
  export MHS_SECRET_CLIENT_KEY=$'client key from NHS Digital here'
  export MHS_SECRET_CA_CERTS=$'ca certs from NHS Digital here'
  ```
  and then run `source configure-env-vars.sh`

* Ensure your OpenTest connectivity is enabled in OpenVPN. (This does not apply if you have an available HSCN connection)
    
* Run `docker-compose up`. This will start the containers which have been built or pulled down, as described above.
   
* Depending on the OS the MHS is being run on, measures may have to be taken to allow public inbound traffic so that
the async responses from Spine can access the MHS. For example on windows a inbound rule may be required in windows
firewall to allow inbound traffic from the Spine through port 443. 

* Note that the `MHS_LOG_LEVEL` environment variable (as documented [here](mhs-adaptor-dev-notes.md#environment-variables)) is set by default to `NOTSET` in the
`docker-compose.yml` file but should be changed if needed.

## Smoke Testing your local MHS and SCR adaptor

The Outbound service, Inbound Service and the Spine Lookup Service all expose a health-check endpoint which can also be
used to facilitate health checks in a load balanced environment.

Each of these services exposes a `/healthcheck` URL which, when called indicates healthy state by returning an empty HTTP 200 response.

In order to determine the ports on `localhost` which these health-check endpoints are listening on, examine your local copy
of the [docker-compose](../docker-compose.yml) file.

## Running MHS components and load balancer with docker

To run the MHS services using docker containers follow the steps below:

1. Make a file in the root call `export-env-vars-and-run-mhs-docker.sh` this name must match to be excluded from git
2. Populate the file with the following information:
  ```sh
#!/bin/bash
LIGHT_GREEN='\033[1;32m'
NC='\033[0m'

echo -e "${LIGHT_GREEN}Exporting environment variables${NC}"

# Your Party key here
export MHS_SECRET_PARTY_KEY=""

# Your endpoint certificate here
export MHS_SECRET_CLIENT_CERT=""

# Your endpoint private key here
export MHS_SECRET_CLIENT_KEY=""

# Endpoint issuing subCA certificate and Root CA certificate here
export MHS_SECRET_CA_CERTS=""

./start-mhs-docker-containers.sh
  ```
3. Populate the environment variables with the certificate details received from NHS OpenTest
4. Execute the script `export-env-vars-and-run-mhs-docker.sh`