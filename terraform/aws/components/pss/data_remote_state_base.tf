data "terraform_remote_state" "base" {
  backend = "s3"
  
  config = {
    bucket = var.tf_state_bucket
    key = "${var.project}-${var.environment}-base.tfstate"
    region = var.region
  }
}

data "terraform_remote_state" "mhs" {
  backend = "azurerm"

  config = {
    resource_group_name = var.tf_state_bucket_resource_group
    storage_account_name = var.tf_state_bucket_storage_account
    container_name = var.tf_state_bucket
    key = "${var.project}-${var.environment}-mhs"
  }
}
