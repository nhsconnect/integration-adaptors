# Terraform
This directory contains the [Terraform](https://www.terraform.io/) configurations used to deploy instances of the MHS
application to AWS.

This configuration will create a full test environment running an MHS application.


## Deploying Manually
In order to manually deploy this environment you will need to first ensure that Terraform can authenticate to AWS. See
the [authentication section of the Terraform AWS documentation](https://www.terraform.io/docs/providers/aws/index.html#authentication)
for details. If running this on your local machine, the simplest option is to
[install the AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-install.html) and run `aws configure`.

Next, you will need to have built the Docker container images containing the MHS. This can be done by running from the root of this repository:
```sh
packer build pipeline/packer/inbound.json
packer build pipeline/packer/outbound.json
```
Note that this will also push the built images to AWS ECR.

Once you have configured AWS authentication, you can run the following commands in this directory:
```
terraform init \
    -backend-config="bucket=<s3_state_bucket>" \
    -backend-config="region=<s3_state_bucket_region>" \
    -backend-config="dynamodb_table=<dynamodb_state_lock_table>"
```
Initialises local Terraform settings. See the [pre-requisites section of the pipeline README](../../README.md#pre-requisites) for details of what is required of the
S3 bucket/DynamoDB table.

```
terraform apply \
    -var environment_id=<deployment_environment_id> \
    -var build_id=<build_id> \
    -var supplier_vpc_id=<supplier_vpc_id> \
    -var opentest_vpc_id=<opentest_vpc_id \
    -var internal_root_domain=<internal_root_domain> \
    -var mhs_outbound_service_instance_count=<no_of_outbound_instances> \
    -var mhs_inbound_service_instance_count=<no_of_inbound_instances> \
    -var task_role_arn=<task_role_arn> \
    -var execution_role_arn=<task_excution_role_arn> \
    -var ecr_address=<docker_registry> \
    -var mhs_log_level=<mhs_log_level> \
    -var mhs_outbound_http_proxy=<optional_MHS_http_proxy_host> \
    -var mhs_state_table_read_capacity=<dynamodb_state_table_read_capacity> \
    -var mhs_state_table_write_capacity=<dynamodb_state_table_write_capacity> \
    -var mhs_sync_async_table_read_capacity=<dynamodb_sync_async_table_read_capacity> \
    -var mhs_sync_async_table_write_capacity=<dynamodb_sync_async_table_read_capacity> \
    -var inbound_queue_host="<inbound_queue_url>" \
    -var inbound_queue_username_arn=<inbound_queue_username_secrets_manager_arn> \
    -var inbound_queue_password_arn=<inbound_queue_password_secrets_manager_arn> \
    -var party_key_arn=<party_key_secrets_manager_arn> \
    -var client_cert_arn=<client_certificate_secrets_manager_arn> \
    -var client_key_arn=<client_certificate_key_secrets_manager_arn> \
    -var ca_certs_arn=<CA_certificates_secrets_manager_arn>
```
Applies the configuration from this directory and deploys. See the descriptions of these variables in
[variables.tf](variables.tf) for details of what each variable represents.

You can remove the resources deployed with:
```
terraform destroy \
    -var environment_id=<deployment_environment_id> \
    -var build_id=<build_id> \
    -var supplier_vpc_id=<supplier_vpc_id> \
    -var opentest_vpc_id=<opentest_vpc_id \
    -var internal_root_domain=<internal_root_domain> \
    -var mhs_outbound_service_instance_count=<no_of_outbound_instances> \
    -var mhs_inbound_service_instance_count=<no_of_inbound_instances> \
    -var task_role_arn=<task_role_arn> \
    -var execution_role_arn=<task_excution_role_arn> \
    -var ecr_address=<docker_registry> \
    -var mhs_log_level=<mhs_log_level> \
    -var mhs_outbound_http_proxy=<optional_MHS_http_proxy_host> \
    -var mhs_state_table_read_capacity=<dynamodb_state_table_read_capacity> \
    -var mhs_state_table_write_capacity=<dynamodb_state_table_write_capacity> \
    -var mhs_sync_async_table_read_capacity=<dynamodb_sync_async_table_read_capacity> \
    -var mhs_sync_async_table_write_capacity=<dynamodb_sync_async_table_read_capacity> \
    -var inbound_queue_host="<inbound_queue_url>" \
    -var inbound_queue_username_arn=<inbound_queue_username_secrets_manager_arn> \
    -var inbound_queue_password_arn=<inbound_queue_password_secrets_manager_arn> \
    -var party_key_arn=<party_key_secrets_manager_arn> \
    -var client_cert_arn=<client_certificate_secrets_manager_arn> \
    -var client_key_arn=<client_certificate_key_secrets_manager_arn> \
    -var ca_certs_arn=<CA_certificates_secrets_manager_arn>
```
