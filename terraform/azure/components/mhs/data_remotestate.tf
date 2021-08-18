data "terraform_remote_state" "base" {
  backend = "azurerm"
  
  config = {
    resource_group_name = var.state_bucket_resource_group
    storage_account_name = var.state_bucket_storage_account
    container_name = var.state_bucket_name
    key = "${var.project}-${var.environment}-base"
  }
}

data "terraform_remote_state" "account" {
  backend = "azurerm"
  
  config = {
    resource_group_name = var.state_bucket_resource_group
    storage_account_name = var.state_bucket_storage_account
    container_name = var.state_bucket_name
    key = "account.tfstate"
  }
}
