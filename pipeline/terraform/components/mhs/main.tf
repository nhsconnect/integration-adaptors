terraform {
  # Store the Terraform state in an S3 bucket
  backend "s3" {
    key = "mhs.tfstate"
  }
}

# Setup AWS provider
provider "aws" {
  version = "~> 2.27"
  profile = "default"
  region = var.region
}