# Pipeline

This directory contains resources related to the CI/CD pipeline used to build the artifacts contained within this repository.

These resources consist of the following directories:
- `packer` - [Packer](https://www.packer.io/) templates used to build machine images used as part of the pipeline
- `scripts`- Custom scripts that are used as part of the pipeline

The pipeline itself is defined in the `Jenkinsfile` in the root of the repository.

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
