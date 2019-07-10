# Pipeline

This directory contains resources related to the CI/CD pipeline used to build the artifacts contained within this repository.

These resources consist of the following directories:
- `packer` - [Packer](https://www.packer.io/) templates used to build container images used as part of the pipeline
- `scripts`- Custom scripts that are used as part of the pipeline
- `terraform` - [Terraform](https://www.terraform.io/) configurations used to deploy the container images used as part of the pipeline

The pipeline itself is defined in the `Jenkinsfile` in the root of the repository.


Several global variables must be set within Jenkins for the scripts to work as part of the build pipeline:

- CLUSTER_ID: The arn of the ecs cluster
- DOCKER_REGISTRY_URL: The address of the ECR ('https://209...')
- DOCKER_REPOSITORY: The ECR arn (209...)
- TASK_EXECUTION_ROLE: The IAM role with the `AmazonECSTaskExecutionRolePolicy` attached to it 
- MHS_ADDRESS: The (private) ip address where the mhs build is running - this will be the private ip of the EC2 instance
    hosting the deployment ECS cluster

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
