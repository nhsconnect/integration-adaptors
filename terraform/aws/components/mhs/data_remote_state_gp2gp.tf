
data "terraform_remote_state" "gp2gp" {
  backend = "s3"
  
  config = {
    bucket = var.tf_state_bucket
    key = "${var.project}-${var.environment}-gp2gp.tfstate"
    region = var.region
  }
}
