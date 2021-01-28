#/bin/bash
set -ex
. ../
terraform init -backend-config='container_name=nia-state-container' -backend-config='storage_account_name=niastate'
terraform plan -var-file=../etc/global.tfvars -var-file=../etc/build1.tfvars