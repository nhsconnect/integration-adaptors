## Azure resource provider ##
terraform {
  required_version = ">= 0.14"

  backend "azurerm" {
    key = "account.tfstate"
  }
}

provider "azurerm" {
  features {
    key_vault {
      purge_soft_delete_on_destroy = true
    }
  }
}
