data "terraform_remote_state" "nhais" {
  backend = "s3"
  
  config = {
    bucket = var.tf_state_bucket
    key = "${var.project}-${var.environment}-nhais.tfstate"
    region = var.region
  }
}