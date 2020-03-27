data "terraform_remote_state" "base" {
  backend = "s3"

  config {
    region = var.region
    bucket = var.terraform_remote_state_bucket

    key = "base.tfstate"
  }
}