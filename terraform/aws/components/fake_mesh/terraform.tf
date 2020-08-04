terraform {
  # Store the Terraform state in an S3 bucket
  backend "s3" {
    # Intentionally blank - all parameters provided in command line
  }
}

# Setup AWS provider
provider "aws" {
  profile = "default"
  version = "~> 2.62"
  region = var.region
}