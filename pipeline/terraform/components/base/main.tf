##################
# Main Terraform file
#
# - Setup Terraform backend
# - configure AWS provider
##################

terraform {
  # Store the Terraform state in an S3 bucket
  backend "s3" {
    key = "base.tfstate"
  }
}

# Setup AWS provider
provider "aws" {
  profile = "default"
  version = "~> 2.27"
  region = var.region
}

# Get the list of availability zones for the selected AWS region
data "aws_availability_zones" "all" {}
