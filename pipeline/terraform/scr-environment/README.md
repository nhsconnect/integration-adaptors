# Terraform
This directory contains the [Terraform](https://www.terraform.io/) configurations used to deploy instances of the SCR
adaptor application to AWS.

This configuration will create an ECS task definition and service for the SCR adaptor and deploy it to the cluster
passed as a parameter.


## Deploying Manually
In order to manually deploy this environment you will need to first ensure that Terraform can authenticate to AWS. See
the [authentication section of the Terraform AWS documentation](https://www.terraform.io/docs/providers/aws/index.html#authentication)
for details. If running this on your local machine, the simplest option is to
[install the AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-install.html) and run `aws configure`.

Next, you will need to have built the Docker container images containing the MHS. This can be done by running the
command `packer build pipeline/packer/scr-web-service.json` in the root of this repository. Note that this will also
push the built images to AWS ECR.

Once you have configured AWS authentication, you can run the following commands in this directory:
```
terraform init \
    -backend-config="bucket=<s3_state_bucket>" \
    -backend-config="region=<s3_state_bucket_region>" \
    -backend-config="dynamodb_table=<dynamodb_state_lock_table>"
```
Initialises local Terraform settings. See the [pre-requisites section of the pipeline README](../../README.md#pre-requisites) for details of what is required of the
S3 bucket/DB table.

```
terraform apply \
    -var environment_id=<deployment_environment_id> \
    -var build_id=<build_id> \
    -var cluster_id=<cluster_id> \
    -var task_execution_role=<task_excution_role_arn> \
    -var ecr_address=<docker_registry> \
    -var scr_log_level=<scr_log_level> \
    -var scr_service_port=<scr_adaptor_listen_port>
```
Applies the configuration from this directory and deploys. See the descriptions of these variables in
[variables.tf](variables.tf) for details of what each variable represents.

You can remove the resources deployed with:
```
terraform destroy \
    -var environment_id=<deployment_environment_id> \
    -var build_id=<build_id> \
    -var cluster_id=<cluster_id> \
    -var task_execution_role=<task_excution_role_arn> \
    -var ecr_address=<docker_registry> \
    -var scr_log_level=<scr_log_level> \
    -var scr_service_port=<scr_adaptor_listen_port>
```
