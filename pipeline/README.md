# Pipeline

This directory contains resources related to the CI/CD pipeline used to build the artifacts contained within this repository.

These resources consist of the following directories:
- `packer` - [Packer](https://www.packer.io/) templates used to build container images used as part of the pipeline
- `scripts`- Custom scripts that are used as part of the pipeline
- `terraform` - [Terraform](https://www.terraform.io/) configurations used to deploy the container images used as part of the pipeline

The pipeline itself is defined in the `Jenkinsfile` in the root of the repository.

# Pre-Requisites

In order to run the build pipeline, the following resources must be created manually:

- An S3 bucket to be used to store the Terraform state database. This allows deployed resources to be re-used in
subsequent builds, reducing the time needed to deploy updated services.
- A DynamoDB table to be used to allow Terraform to lock the shared state, preventing issues if concurrent deployments
of the same environment are performed. The table must have a primary key named LockID.

# Jenkins

We are running a Jenkins master instance as an ECS Docker container. This is configured to, via the [amazon-ecs plugin], spin up Jenkins worker ECS Docker containers to run the pipeline.

In order to achieve this, a number of components are required:
- there are some subfolders in the `packer` folder with files for creating the Docker images for the Jenkins master and workers.
- when configuring the [amazon-ecs plugin], some credentials need to be provided that can be used to create/destroy the Jenkins workers. This can be done by creating an IAM role following the information [here][amazon-ecs plugine] in the _IAM role_ section. The IAM role should have the trust policy:
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
- the Jenkins workers need their own IAM role that has sufficient permissions to run the build job.

[amazon-ecs plugin]: https://wiki.jenkins.io/display/JENKINS/Amazon+EC2+Container+Service+Plugin

### Permissions and global variables

Several global variables must be set within Jenkins for the scripts to work as part of the build pipeline:

- ASID: The asid associated with the mhs instance (this is provided with opentest creds)
- CLUSTER_ID: The arn of the ecs cluster
- DOCKER_REGISTRY_URL: The address of the ECR ('https://209...')
- DOCKER_REPOSITORY: The ECR arn (209...)
- TASK_EXECUTION_ROLE: The IAM role with the `AmazonECSTaskExecutionRolePolicy` attached to it 
- MHS_ADDRESS: The (private) ip address where the mhs build is running - this will be the private ip of the EC2 instance
    hosting the deployment ECS cluster
- SCR_REPOSITORY: The docker repository used to upload and retrieve the SCRWebService images
- SCR_REPOSITORY_URL: Same as above with the full URL
- SCR_SERVICE_ADDRESS: The endpoint address the SCRWebService can be reached on e.g `http://192.168.41.129:9000`
- SCR_SERVICE_PORT: The port the SCR endpoint is expected to be on
- SONAR_HOST: The URL for the sonarqube server.
- SONAR_TOKEN: The login token to use when submitting jobs to sonarqube.
- TF_STATE_BUCKET: The name of an S3 bucket to use to store Terraform state in. As described in
[Pre-Requisites](#pre-requisites)
- TF_STATE_BUCKET_REGION: The region that the Terraform state S3 bucket (as described in
[Pre-Requisites](#pre-requisites)) resides in.
- TF_STATE_FILE: The name of the file within the S3 bucket (as described in [Pre-Requisites](#pre-requisites)) to store
terraform state in
- TF_LOCK_TABLE_NAME: The name of the DynamoDB table Terraform should use to enable locking of state (as described in
[Pre-Requisites](#pre-requisites)).

The Jenkins worker EC2 instance will have to have the following permission in order to publish the builds to 
ECR and start the tasks in ECS with terraform:

- ecs:DescribeServices
- ecs:CreateService
- ecs:DeleteService
- ecs:UpdateService
- ecs:DescribeTaskDefinition
- ecs:DeregisterTaskDefinition
- ecs:RegisterTaskDefinition
- ecr:UploadLayerPart
- ecr:CompleteLayerUpload
- ecr:PutImage
- ecr:InitiateLayerUpload
- iam:PassRole
	

The role associated with the box should also have the `AmazonECSTaskExecutionRolePolicy` and 
`AmazonEC2ContainerServiceforEC2Role` policies.

The EC2 instance running the mhs build (to run the integration tests against) must have the opentest connection 
established using the Fabric script in `scripts`. The open test certs and party key files should be copied
to the EC2 instance in a `home/ec2-user/certs` directory (this directory is a shared volume with the running 
mhs docker container as specified in the docker container). 


There must also be log groups in Cloudwatch under the following names - these groups need to be created manually:
- `/ecs/jenkins-master`
- `/ecs/jenkins-workers-jenkins-worker`
- `/ecs/scr-service-environment`
- `/ecs/sonarqube`
- `/ecs/test-environment`