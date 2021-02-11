## Azure resource provider ##
terraform {
  required_version = ">= 0.14"

  backend "azurerm" {
    key = "nhais.tfstate"
  }
}

provider "kubernetes" {
  client_certificate     = base64decode(data.terraform_remote_state.base.outputs.base_aks_client_certificate)
  client_key             = base64decode(data.terraform_remote_state.base.outputs.base_aks_client_key)
  cluster_ca_certificate = base64decode(data.terraform_remote_state.base.outputs.base_aks_cluster_ca_certificate)
  #host                   = data.terraform_remote_state.base.outputs.base_aks_host

  # For running terraform on private cluster, comment out the "host" above, and uncommnet below:
  host = "https://localhost:8443"
  # for setting up the tunnel, run the "kube_tunnel" from base output
  # ssh -L 8443:build1-cd9cf5b4.72ce1d8a-84b4-46e2-af89-8a21998de3f0.privatelink.ukwest.azmk8s.io:443 azure-build1-testbox
}

provider "azurerm" {
  features {
    key_vault {
      purge_soft_delete_on_destroy = true
    }
  }
}
