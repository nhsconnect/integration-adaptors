# Terraform
This directory contains the [Terraform](https://www.terraform.io/) configurations used to deploy instances of the MHS
application to AWS' ECS service for integration testing as part of the build pipeline.

This configuration will create a new ECS task definition referencing the Docker container image provided as a parameter
and then create a new ECS service in a pre-existing cluster (again, provided as a parameter) which will run a single
instance of the container image. 

## Pre-requisites
In order to function, this configuration expects several components to exist in the AWS account being used: 

- An IAM role for the 'Elastic Container Service Task' trusted entity with the built-in
  `AmazonECSTaskExecutionRolePolicy`. You can use the `ecsTaskExecutionRole` created for you automatically by AWS when
  creating a task definition from the console, if available. This ARN of this role is passed as the
  `task_execution_role` input variable.
- An IAM role for the EC2 instance/etc. running the build pipeline. This must grant the `ecs:RegisterTaskDefinition`
  ,`ecs:CreateService`, `iam:PassRole`, `ecs:DescribeTaskDefinition`, `ecs:DeregisterTaskDefinition`, 
  `ecs:DescribeServices`, `ecs:UpdateService` & `ecs:DeleteService` permissions to the build machine.
- A CloudWatch log group named `/ecs/test-environment`
- An ECS Cluster - the ARN of this cluster must be passed as the `cluster_id` input variable

## Deploying Manually
In order to manually deploy this environment you will need to first ensure that Terraform can authenticate to AWS. See
the [authentication section of the Terraform AWS documentation](https://www.terraform.io/docs/providers/aws/index.html#authentication)
for details. If running this on your local machine, the simplest option is to
[install the AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-install.html) and run `aws configure`.

Next, you will need to have built the Docker container image containing the MHS. This can be done using the
`pipeline/packer/mhs.json` script.  

Once you have configured AWS authentication, you can run the following commands in this directory:
1. `terraform init` - Initialises local Terraform settings 
1. `terraform apply --var cluster_id=<cluster-arn> -var task_execution_role=<role-arn> -var build_id=<build-tag>` - Applies the configuration from this directory and deploys

You can remove the resources deployed with `terraform destroy --var cluster_id=<cluster-arn> -var task_execution_role=<role-arn> -var build_id=<build-tag>` 