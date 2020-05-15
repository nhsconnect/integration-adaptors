# Pipeline

This directory contains infrastructure automation used to build the artifacts contained within this repository.

These resources can be used to provide infrastructure automation in two ways:
1. To enable a full software delivery pipeline where the MHS Alpha software itself is being developed. In
this context, the terraform will likely to executed from a CI/CD solution such as Jenkins to enable
automated integration testing to take place against a deployed instance.
2. To stand up the AWS exemplar outside of the CI/CD pipeline. It will be necessary to set up various terraform variables using the `terraform.tfvars` 
file.

These resources consist of the following directories:
- `packer` - [Packer](https://www.packer.io/) templates used to build container images used as part of the pipeline
- `scripts`- Custom scripts which support build and deployment of resources.
- `terraform` - [Terraform](https://www.terraform.io/) contains Terraform assets which targeting AWS deployments through
the AWS provider for Terraform.

The pipeline itself is defined in the `Jenkinsfile` in the root of the repository.

# Pre-Requisites for build pipeline

In order to run the build pipeline, the following resources must be created manually:

- An S3 bucket to be used to store the Terraform state databases for the MHS & SCR configurations. This allows deployed resources to be re-used in
subsequent builds, reducing the time needed to deploy updated services.
    - It is recommended that default encryption of objects in this bucket is enabled when creating it
- Two DynamoDB tables to be used to allow Terraform to lock the shared state of the MHS & SCR configurations, preventing issues if concurrent deployments
of the same environment are performed. These tables must have a primary key named `LockID`.

   Alternatively create MongoDB instance which will be used instead of DynamoDB. 
   There is no need of creating any MongoDB databases nor collections - they will be created automatically.
   Type of DB can be choosen by env var `MHS_PERSISTENCE_ADAPTOR: dynamodb(default)|mongodb`
- Log groups in Cloudwatch under the following names:
    - `/ecs/jenkins-master`
    - `/ecs/jenkins-workers-jenkins-worker`
    - `/ecs/scr-service-environment`
    - `/ecs/sonarqube`
- ECR repositories with the following names:
    - `mhs/inbound`
    - `mhs/outbound`
    - `mhs/route`
    - `scr-web-service`
- An IAM role to allow the ECS service to execute ECS tasks. This must be a service role (see the
[AWS documentation on creating roles for AWS services](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_create_for-service.html))
with the trusted entity set to 'Elastic Container Service Task' with the built-in `AmazonECSTaskExecutionRolePolicy`.
You can use the `ecsTaskExecutionRole` created for you automatically by AWS when creating a task definition from the
console, if available.
  - This role also needs a policy to allow it to fetch the required secrets from AWS secrets manager (see below for
  details of the required secrets). This policy should look like:
```
  {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "VisualEditor0",
            "Effect": "Allow",
            "Action": "secretsmanager:GetSecretValue",
            "Resource": [
                "list of secret ARNs here"
            ]
        }
    ]
}
```
- An IAM role to allow the ECS service to auto-scale ECS tasks. This must be a service role (see the
[AWS documentation on creating roles for AWS services](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_create_for-service.html))
with the trusted entity set to 'Elastic Container Service Autoscale' which has the AWS managed
'AmazonEC2ContainerServiceAutoscaleRole' policy assigned to it. This can be created by following the AWS documentation
on the [Amazon ECS Service Auto Scaling IAM Role](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/autoscale_IAM_role.html)
- An IAM role for the MHS containers to use to run as (the `TASK_ROLE` mentioned [below](#global-variables-for-jenkins-pipeline)).
This must be a service role (see the
[AWS documentation on creating roles for AWS services](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_create_for-service.html))
with the trusted entity set to 'Elastic Container Service Task' and have the policy:
```
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "VisualEditor0",
            "Effect": "Allow",
            "Action": [
                "dynamodb:BatchGetItem",
                "dynamodb:BatchWriteItem",
                "dynamodb:ConditionCheckItem",
                "dynamodb:PutItem",
                "dynamodb:DeleteItem",
                "dynamodb:GetItem",
                "dynamodb:Scan",
                "dynamodb:Query",
                "dynamodb:UpdateItem"
            ],
            "ARNs of DynamoDB tables to allow access to"
        }
    ]
}
```
- An IAM role for the ECS task (i.e Jenkins worker) running the build pipeline. This must be a service role (see the
[AWS documentation on creating roles for AWS services](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_create_for-service.html))
with the trusted entity set to 'Elastic Container Service Task' which includes the following AWS managed IAM policies, in order to allow the built
containers to be published to ECR and the integration test environment to be stood up by Terraform:
    - AmazonS3FullAccess
    - AmazonVPCFullAccess
    - ElasticLoadBalancingFullAccess
    - AmazonEC2ContainerRegistryPowerUser
    - AmazonECS_FullAccess
    - AmazonDynamoDBFullAccess (only if DynamoDB is used)
    - CloudWatchLogsFullAccess
    - AmazonRoute53FullAccess
    - AmazonElastiCacheFullAccess
- An ECS Cluster for the SCR application to be deployed into. This must be an EC2 Linux cluster.
- Two TLS certificates. One to be used for the outbound load balancer and one for the route load balancer
    - These certificates should be stored in AWS Certificate Manager (they can either be requested through Certificate
    Manager, or imported into it)
    - If you wish to use self-signed certificates, these can be generated using OpenSSL with the following command:
    `openssl req -x509 -subj //CN=<lb-hostname> -newkey rsa:<key-length> -nodes -keyout key.pem -out cert.pem -days <days-until-expiry>`
        - Where route-lb-hostname is the DNS name of the load balancer. This is
        `mhs-outbound.<environment-id>.<internal_root_domain>` for the outbound load balancer and
        `mhs-route.<environment-id>.<internal_root_domain>` for the route load balancer, where `environment-id` and
        `<internal_root_domain>` are the variables provided to Terraform when deploying the exemplar blueprint.
        - Where key-length is the length of the RSA key (in bits) to use for the certificate
        - Where days-until-expiry is the number of days the generated certificate should be valid for
        - e.g: `openssl req -x509 -subj //CN=mhs-outbound.example-environment.myteam.example.com -newkey rsa:2048 -nodes -keyout key.pem -out cert.pem -days 365`
- Entries in AWS Secrets Manager for all sensitive data. These entries should be created by following the [AWS tutorial
on storing secrets](https://docs.aws.amazon.com/secretsmanager/latest/userguide/tutorials_basic.html#tutorial-basic-step1),
selecting to store the secret as "Other type of secrets" and entering the required value using the plaintext tab (these
values should not be specified as JSON). The following secrets are required:
    - The username to use when connecting to the AMQP inbound queue
    - The password to use when connecting to the AMQP inbound queue
    - The party key associated with your MHS
    - The client certificate the outbound MHS component should present to other MHS instances
    - The private key for the client certificate the outbound MHS component should present to other MHS instances
    - (Optional) The CA certificates used to validate the certificates presented by the MHS. This value is required if
    the certificate you have used for the outbound load balancer (above) is not signed by a legitimate CA. If you have
    used a self-signed certificate, this value can be that certificate.
    - (Optional) The CA certificates used to validate the certificate presented by the MHS' route service. This value is required if
    the certificate you have used for the route load balancer (above) is not signed by a legitimate CA. If you have
    used a self-signed certificate, this value can be that certificate.

# Jenkins based CI/CD pipeline setup

The MHS Adaptor was built using Jenkins. To replicate this setup, follow the instructions below:

Set up a master Jenkins instance as an ECS Docker container. This is configured to, via the [amazon-ecs plugin], spin up Jenkins worker ECS Docker containers to run the pipeline.

In order to achieve this, a number of components are required:
- there are some subfolders in the `packer` folder with files for creating the Docker images for the Jenkins master and workers.
- when configuring the [amazon-ecs plugin], some credentials need to be provided that can be used to create/destroy the Jenkins workers. This can be done by creating an IAM role following the information [here][amazon-ecs plugin] in the _IAM role_ section. The IAM role should have the trust policy:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "",
      "Effect": "Allow",
      "Principal": {
        "Service": "ecs-tasks.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
```
I found I also needed to add a permission policy that looked like:
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "VisualEditor0",
            "Effect": "Allow",
            "Action": "iam:PassRole",
            "Resource": "arn:aws:iam::<account id>:role/ecsTaskExecutionRole"
        }
    ]
}
```
where `ecsTaskExecutionRole` is a default role created when creating task definitions.
- The Jenkins worker EC2 instance must have an IAM role assigned, as described in [the pre-requisites](#pre-requisites-for-build-pipeline)
section above.

[amazon-ecs plugin]: https://wiki.jenkins.io/display/JENKINS/Amazon+EC2+Container+Service+Plugin

## Global variables for Jenkins pipeline

Several global environment variables must be set within Jenkins for the scripts to work as part of the build pipeline:

- INTEGRATION_TEST_ASID: The asid associated with the mhs instance (this is provided with NHS Digital OpenTest credentials)
- CLUSTER_ID: The arn of the ecs cluster the SCR application should be deployed into (as described in
[Pre-Requisites](#pre-requisites-for-build-pipeline))
- DOCKER_REGISTRY: The address of the Docker registry to publish built containers to. e.g. `randomid.dkr.ecr.eu-west-2.amazonaws.com` This should not include an `http://` prefix, or repository names/paths.
- TASK_ROLE: The IAM role that will be applied to the running MHS container tasks (as described in
[Pre-Requisites](#pre-requisites-for-build-pipeline)).
- TASK_EXECUTION_ROLE: The IAM role with the `AmazonECSTaskExecutionRolePolicy` attached to it (as described in
[Pre-Requisites](#pre-requisites-for-build-pipeline)).
- TASK_SCALING_ROLE: The IAM role to grant ECS permissions to auto-scale services (as described in
[Pre-Requisites](#pre-requisites-for-build-pipeline)).
- SCR_SERVICE_ADDRESS: The endpoint address the SCRWebService can be reached on e.g `http://192.168.41.129:9000`
- SCR_SERVICE_PORT: The port the SCR endpoint is expected to be on
- SONAR_HOST: The URL for the sonarqube server.
- SONAR_TOKEN: The login token to use when submitting jobs to sonarqube.
- TF_STATE_BUCKET: The name of an S3 bucket to use to store both MHS & SCR Terraform state in (as described in
[Pre-Requisites](#pre-requisites-for-build-pipeline)).
- TF_STATE_BUCKET_REGION: The region that the Terraform state S3 bucket (as described in
[Pre-Requisites](#pre-requisites-for-build-pipeline)) resides in.
- TF_MHS_LOCK_TABLE_NAME: The name of the DB table Terraform should use to enable locking of state (as described in
[Pre-Requisites](#pre-requisites-for-build-pipeline)).
- TF_SCR_LOCK_TABLE_NAME: The name of the DB table Terraform should use to enable locking of state (as described in
[Pre-Requisites](#pre-requisites-for-build-pipeline)).
- SUPPLIER_VPC_ID: The ID of the VPC that represents the supplier system that will connect to the MHS
- OPENTEST_VPC_ID: The ID of the VPC that contains the machine which manages the Opentest connection to Spine
- INTERNAL_ROOT_DOMAIN: The domain name to be used internally to refer to parts of the MHS (subdomains will be created
from this root domain). This domain name should not clash with any domain name on the internet. e.g.
internal.somedomainyoucontrol.com"
- MHS_OUTBOUND_HTTP_PROXY: The hostname of the HTTP proxy being used to route connections to Spine. E.g. an Opentest
proxy machine.
- MHS_OUTBOUND_VALIDATE_CERTIFICATE: Verification of the server certificate received when making a connection to the spine MHS.
- MHS_INBOUND_QUEUE_BROKERS: The url(s) of the amqp inbound queue broker(s). e.g. `amqps://example.com:port`. Note that if
the amqp connection being used is a secured connection (which it should be in production), then the url should start
with `amqps://` and not `amqp+ssl://`. This URL should not include the queue name. Can be a coma-separated list or urls for HA
- MHS_INBOUND_QUEUE_NAME: The name of the queue on the broker identified by `MHS_INBOUND_QUEUE_BROKERS` to place inbound
messages on. e.g `queue-name`
- INBOUND_QUEUE_USERNAME_ARN: The ARN (in secrets manager) of the username to use when connecting to the AMQP inbound
queue.
- MHS_SECRET_INBOUND_QUEUE_USERNAME: The username to use when connecting to the AMQP inbound queue (used by the integration
tests)
- MHS_SECRET_INBOUND_QUEUE_PASSWORD: The password to use when connecting to the AMQP inbound queue (used by the integration
tests)
- INBOUND_QUEUE_PASSWORD_ARN: The ARN (in secrets manager) of the password to use when connecting to the AMQP inbound
queue.
- PARTY_KEY_ARN: The ARN (in secrets manager) of the party key associated with your MHS.
- CLIENT_CERT_ARN: The ARN (in secrets manager) of the client certificate the outbound MHS should present.
- CLIENT_KEY_ARN: The ARN (in secrets manager) of the private key for the client certificate identified by
`CLIENT_CERT_ARN`
- CA_CERTS_ARN: The ARN (in secrets manager) of the CA certificates used to validate the certificates presented by
incoming connections to the MHS.
- OUTBOUND_ALB_CERT_ARN: The ARN (in AWS Certificate Manager) of the certificates the outbound ALB should present.
- ROUTE_ALB_CERT_ARN: The ARN (in AWS Certificate Manager) of the certificates the outbound ALB should present.
- ROUTE_CA_CERTS_ARN: The ARN (in secrets manager) of the CA certificates used to validate the certificates presented by
the Spine Route Lookup service.
- OUTBOUND_CA_CERTS_ARN: The ARN (in secrets manager) of the CA certificates used to validate the certificates presented
by the outbound service's load balancer.
- SPINE_ORG_CODE: The organisation code for the Spine instance that your MHS is communicating with. E.g `YES`
- SPINEROUTELOOKUP_SERVICE_LDAP_URL: The URL the Spine Route Lookup service should use to communicate with SDS.
e.g. `ldaps://example.com`
- SPINEROUTELOOKUP_SERVICE_SEARCH_BASE: The LDAP location the Spine Route Lookup service should use as the base of its
searches when querying SDS. e.g. `ou=services,o=nhs`. This value should not contain whitespace.
- SPINEROUTELOOKUP_SERVICE_DISABLE_TLS: An optional flag. If set to exactly `True`, TLS will be disabled for SDS
requests.
* MHS_FORWARD_RELIABLE_ENDPOINT_URL: The URL for MHS outbound to communicate with Spine for Forward Reliable messaging
