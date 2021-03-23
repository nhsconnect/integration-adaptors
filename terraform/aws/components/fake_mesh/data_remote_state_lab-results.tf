
data "terraform_remote_state" "lab-results" {
  backend = "s3"
  
  config = {
    bucket = var.tf_state_bucket
    key = "${var.project}-${var.environment}-lab-results.tfstate"
    region = var.region
  }
}
