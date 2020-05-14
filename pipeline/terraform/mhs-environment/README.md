# Terraform
This directory contains the [Terraform](https://www.terraform.io/) configurations used to deploy instances of the MHS
application to AWS.

This configuration will create a full test environment running an MHS application.

## Known Issues
- There is an [issue](https://github.com/terraform-providers/terraform-provider-aws/issues/8561) using Terraform to
deploy the ElastiCache replication group defined in [`elasticache.tf`](elasticache.tf). If the `environment_id` variable
provided to Terraform is too long, attempting to create the replication group with encryption in transit enabled results
in a failure with the replication group's state being reported as `create-failed`. You can avoid this issue by ensuring
that the value you use for `environment_id` is no longer than 20 characters.

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
S3 bucket/DB table.

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
    -var mhs_outbound_validate_certificate=<True/False> \
    -var mhs_state_table_read_capacity=<dynamodb_state_table_read_capacity> \
    -var mhs_state_table_write_capacity=<dynamodb_state_table_write_capacity> \
    -var mhs_sync_async_table_read_capacity=<dynamodb_sync_async_table_read_capacity> \
    -var mhs_sync_async_table_write_capacity=<dynamodb_sync_async_table_read_capacity> \
    -var inbound_queue_brokers="<inbound_queue_brokers>" \
    -var inbound_queue_name="<inbound_queue_name>" \
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
    -var mhs_outbound_validate_certificate=<True/False> \
    -var mhs_state_table_read_capacity=<dynamodb_state_table_read_capacity> \
    -var mhs_state_table_write_capacity=<dynamodb_state_table_write_capacity> \
    -var mhs_sync_async_table_read_capacity=<dynamodb_sync_async_table_read_capacity> \
    -var mhs_sync_async_table_write_capacity=<dynamodb_sync_async_table_read_capacity> \
    -var inbound_queue_brokers="<inbound_queue_brokers>" \
    -var inbound_queue_name="<inbound_queue_name>" \
    -var inbound_queue_username_arn=<inbound_queue_username_secrets_manager_arn> \
    -var inbound_queue_password_arn=<inbound_queue_password_secrets_manager_arn> \
    -var party_key_arn=<party_key_secrets_manager_arn> \
    -var client_cert_arn=<client_certificate_secrets_manager_arn> \
    -var client_key_arn=<client_certificate_key_secrets_manager_arn> \
    -var ca_certs_arn=<CA_certificates_secrets_manager_arn>
```

### Supplier/Opentest VPC config
Note that the Terraform config in this folder has only the minimal config to connect the MHS VPC
with the supplier and Opentest VPCs (ie create a VPC peering connection and configure the route
tables of all VPCs). Any further configuration to allow inbound/outbound requests between the
VPCs must be done manually.

In practice, this means that:
- the supplier VPC needs to:
  - allow outbound traffic on port 80 to the MHS outbound load balancer
  - allow inbound traffic on port 5671 to the Amazon MQ instance
  - Have DNS hostnames enabled
- the Opentest VPC needs to:
  - allow outbound traffic on port 443 to the MHS inbound load balancer for requests/responses
  from Spine
  - allow inbound traffic from the MHS VPC on port 3128 for the HTTP proxy
  - allow inbound traffic from the MHS VPC on port 389 for LDAP requests
  - Have DNS hostnames enabled

Also note that the MHS VPC uses the private ip address cidr block 10.0.0.0/16. The supplier
and Opentest VPCs will need to use non-overlapping cidr blocks in order for the VPC
peering connections to successfully be created.

### HTTPS on load balancers
The MHS inbound load balancer passes through TLS traffic down to the Fargate tasks which
terminate the TLS connection. The MHS outbound and MHS route load balancers, however, are
HTTP load balancers and don't by default do any TLS termination. This can be configured in
AWS. To do this requires:
- configuring certificates to use in [AWS Certificate Manager](https://aws.amazon.com/certificate-manager/)
- modifying the load balancers to use these certificates to do SSL termination
- configuring the supplier system and MHS outbound to validate these certificates as
  appropriate when making requests to these load balancers (this is only required if the
  certificates aren't trusted by default ie if the certificates are not issued by a publicly
  trusted CA).
- Altering the following security groups for the load balancers to allow HTTPS traffic
  instead of HTTP, and for MHS outbound to allow downstream HTTPS requests to the MHS route
  load balancer:
  - `aws_security_group.alb_outbound_security_group`
  - `aws_security_group.alb_route_security_group`
  - `aws_security_group_rule.mhs_outbound_security_group_route_egress_rule`
