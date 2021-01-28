#/bin/bash
#set -e
terraform init
terraform plan --var-file=../etc/global.tfvars
terraform apply --var-file=../etc/global.tfvars