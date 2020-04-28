#!/bin/bash
# vim: set syntax=sh tabstop=2 softtabstop=2 shiftwidth=2 expandtab smarttab :

# -u          :: Fail on unbounded variable usage
# -o pipefail :: Report failures that occur elsewhere than just the last command in a pipe
# set -uo pipefail

# Just for logging. Because rsyslog is not running before userdata.
# log_file='/tmp/bootstrap.log';

# function log() {
#   echo -e "$(date) ${1}" \
#     | tee -a "/tmp/bootstrap.log";
# }

# function error() {
#   echo -e "$(date) ERROR: ${1}" \
#     | tee -a "/tmp/bootstrap.log";
#   exit 1;
# };

export aws="$(which aws || echo '/usr/bin/aws')";
export curl="$(which curl || echo '/usr/bin/curl')";

# log "installing EPEL"
# yum install -y https://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm
# yum-config-manager --enable epel

echo "Installing docker, git, ssh"

yum makecache
yum install -y docker git ssh

echo "Installing docker compose"
curl -L "https://github.com/docker/compose/releases/download/1.25.5/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
ln -s /usr/local/bin/docker-compose /usr/bin/docker-compose

service docker start

echo "Cloning the NHS repo from ${GIT_REPO} branch ${GIT_BRANCH}"

mkdir -p /opt/NHS
cd /opt/NHS
git clone ${GIT_REPO}
cd integration-adaptors
git fetch
git checkout ${GIT_BRANCH}

echo "Building the image with tag ${BUILD_TAG}"
docker build -t local/fake-spine:${BUILD_TAG} -f ./integration-tests/fake_spine/Dockerfile .

echo "Starting the image"
./integration-tests/setup_component_test_env.sh
. ./component-test-source.sh # Load the deafult env variables from the test set
. /var/variables_source.sh   # Override with ones supplied by TF
# BUILD_TAG=${BUILD_TAG} docker-compose -f docker-compose.ec2.override.yml up -d fakespine
docker run \
 -e INBOUND_SERVER_BASE_URL \
 -e FAKE_SPINE_OUTBOUND_DELAY_MS \
 -e FAKE_SPINE_INBOUND_DELAY_MS \
 -e FAKE_SPINE_OUTBOUND_SSL_ENABLED \
 -e FAKE_SPINE_PORT \
 -e FAKE_SPINE_PROXY_VALIDATE_CERT \
 -e FAKE_SPINE_PRIVATE_KEY \
 -e FAKE_SPINE_CERTIFICATE \
 -e FAKE_SPINE_CA_STORE \
 -e MHS_SECRET_PARTY_KEY \
 -e MHS_LOG_LEVEL \
 --log-driver=awslogs --log-opt awslogs-region=eu-west-2 --log-opt awslogs-group=/aws/ec2/fake-spine-ec2-instance --log-opt awslogs-create-group=true \
 -d -p 80:80 443:443 \
 local/fake-spine:${BUILD_TAG}

echo "Sleep 20s"
sleep 20s

echo "Show the logs of started container"
docker logs `docker ps -n 1 --format '{{.ID}}'`


