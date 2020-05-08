data "terraform_remote_state" "mhs" {
  backend = "s3"
  
  config = {
    bucket = var.mhs_state_bucket
    key = "${var.environment_id}-mhs.tfstate"
    region = var.region
  }
}