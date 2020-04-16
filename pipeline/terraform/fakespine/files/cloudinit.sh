  #!/bin/bash
# vim: set syntax=sh tabstop=2 softtabstop=2 shiftwidth=2 expandtab smarttab :

# -u          :: Fail on unbounded variable usage
# -o pipefail :: Report failures that occur elsewhere than just the last command in a pipe
set -uo pipefail

# Just for logging. Because rsyslog is not running before userdata.
log_file='/tmp/bootstrap.log';

function log() {
  echo -e "$(date) ${1}" \
    | tee -a "${log_file}";
}

function error() {
  echo -e "$(date) ERROR: ${1}" \
    | tee -a "${log_file}";
  exit 1;
};

export aws="$(which aws || echo '/usr/bin/aws')";
export curl="$(which curl || echo '/usr/bin/curl')";

log "Installing docker, git, ssh"

yum install -y docker git ssh

log "Cloning the NHS repo"

mkdir -p /opt/NHS
cd /opt/NHS
git clone git@github.com:nhsconnect/integration-adaptors.git
cd integration-adaptors
git fetch
git checkout feature/NIAD-132-fake-spine-vnp-deploy

log "Building the image"
BUILD_TAG=foo
docker build -t local/fake-spine:${BUILD_TAG} -f ./integration-tests/fake_spine/Dockerfile .

log "Starting the image"
./setup_component_test_env.sh
. ./component-test-source.sh
BUILD_TAG=foo docker-compose -f docker-compose.yml up fakespine



