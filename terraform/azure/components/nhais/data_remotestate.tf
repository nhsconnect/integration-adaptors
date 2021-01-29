data "terraform_remote_state" "base" {
  backend = "azurerm"
  
  config = {
    storage_account_name = var.state_bucket_storage_account
    container_name = var.state_bucket_name
    key = "base.tfstate"
  }
}
