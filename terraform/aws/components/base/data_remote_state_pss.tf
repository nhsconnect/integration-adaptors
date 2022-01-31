data "terraform_remote_state" "pss" {
  backend = "s3"
  
  config = {
    bucket = var.tf_state_bucket
    key = "${var.project}-${var.environment}-pss.tfstate"
    region = var.region
  }
}