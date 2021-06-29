## AKS kubernetes cluster ##
resource "azurerm_kubernetes_cluster" "base_aks" { 
  #name                = var.cluster_name
  name                = "${local.resource_prefix}-aks_cluster"
  resource_group_name = data.terraform_remote_state.account.outputs.resource_group_name
  location            = data.terraform_remote_state.account.outputs.resource_group_location
  kubernetes_version = "1.18.17" //
  dns_prefix          = var.environment
  private_cluster_enabled = var.private_cluster
  # Note: be careful with these, the creation time of AKS is very long and times out under terraform
  # Better to create AKS, and them enable the ranges if needed
  # api_server_authorized_ip_ranges = concat(
  #   var.jumpbox_allowed_ips,
  #   ["${azurerm_linux_virtual_machine.base_jumpbox.public_ip_address}/32"],
  #   ["${azurerm_linux_virtual_machine.base_jumpbox.private_ip_address}/32"]
  # )

  linux_profile {
    admin_username = var.aks_admin_user

    ## SSH key is generated using "tls_private_key" resource
    ssh_key {
      key_data = "${trimspace(tls_private_key.key.public_key_openssh)} ${var.aks_admin_user}@azure.com"
    }
  }

  addon_profile {
    http_application_routing {
      enabled = false
    }

    kube_dashboard {
      enabled = true
    }
  }
  
  default_node_pool {
    name = "default"
    node_count = var.aks_node_count
    vm_size    = "Standard_F4s_v2"
    os_disk_size_gb = 30
    vnet_subnet_id = azurerm_subnet.base_aks_subnet.id
  }

  network_profile {
    network_plugin     = "azure"
    network_policy     = "azure"
    service_cidr       = var.base_aks_internal_cidr
    dns_service_ip     = var.base_aks_internal_dns
    docker_bridge_cidr = var.base_aks_docker_bridge_cidr
    outbound_type      = "userDefinedRouting"
  }

  service_principal {
    client_id     = var.client_id
    client_secret = var.client_secret
  }

  tags = merge(local.default_tags,{
    Name = "${local.resource_prefix}-aks_cluster"
  })

  depends_on = [
    azurerm_subnet.base_aks_subnet,
    azurerm_route_table.base_route_table,
    azurerm_subnet_route_table_association.base_aks_subnet_association,
    azurerm_route.base_default_route,
  ]
}

# https://github.com/Azure/AKS/issues/1557
# resource "azurerm_role_assignment" "vmcontributor" {
#   role_definition_name = "Virtual Machine Contributor"
#   scope                = azurerm_resource_group.mhs_adaptor.name
#   principal_id         = azurerm_kubernetes_cluster.base_aks.identity[0].principal_id
# }
