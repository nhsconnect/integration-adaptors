# Description on contents

## [aws](aws/README.md) - Terraform code for AWS deployments of adaptors

## [azure](azure/README.md) - Terraform code for Azure deployments of adaptors

## Jenkinsfiles

  Groovy jenkinsfile used to plan / apply / destroy terraform on AWS. In order for that to work the Jenkins instance from which the pipeline is run needs to exist on the same account as applied resources, and have correct IAM instance profile that allows it to make changes to infrastructure.
