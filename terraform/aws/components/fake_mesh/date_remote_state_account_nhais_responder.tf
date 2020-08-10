data "terraform_remote_state" "nhais_responder" {
  backend = "s3"
  
  config = {
    bucket = var.tf_state_bucket
    key = "${var.project}-${var.environment}-nhais_responder.tfstate"
    region = var.region
  }
}