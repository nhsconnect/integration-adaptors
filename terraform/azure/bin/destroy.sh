#/bin/bash
#set -e
terraform init
terraform plan --destroy --var-file=../etc/global.tfvars
terraform destroy --var-file=../etc/global.tfvars