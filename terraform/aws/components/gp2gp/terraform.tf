terraform {
  # Store the Terraform state in an S3 bucket
  backend "s3" {
    # Intentionally blank - all parameters provided in command line
  }
}

# Setup AWS provider
provider "aws" {
  profile = "default"
  region = var.region
}
