# Pipeline

This directory contains resources related to the CI/CD pipeline used to build the artifacts contained within this repository.

These resources consist of the following directories:
- `packer` - [Packer](https://www.packer.io/) templates used to build container images used as part of the pipeline
- `scripts`- Custom scripts that are used as part of the pipeline
- `terraform` - [Terraform](https://www.terraform.io/) configurations used to deploy the container images used as part of the pipeline

The pipeline itself is defined in the `Jenkinsfile` in the root of the repository.
