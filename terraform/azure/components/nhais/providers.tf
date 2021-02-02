## Azure resource provider ##
terraform {
  required_version = ">= 0.14"

  backend "azurerm" {
    #resource_group_name  = var.state_bucket_resource_group
    #storage_account_name = var.state_bucket_storage_account
    #container_name       = var.state_bucket_name
    key                  = "nhais.tfstate"
  }
}

provider "kubernetes" {
  host                   = data.terraform_remote_state.base.outputs.base_aks_host
  client_certificate     = base64decode(data.terraform_remote_state.base.outputs.base_aks_client_certificate)
  client_key             = base64decode(data.terraform_remote_state.base.outputs.base_aks_client_key)
  cluster_ca_certificate = base64decode(data.terraform_remote_state.base.outputs.base_aks_cluster_ca_certificate)
}

provider "azurerm" {
  #version = "~>2.5"
  features {
    key_vault {
      purge_soft_delete_on_destroy = true
    }
  }
}
