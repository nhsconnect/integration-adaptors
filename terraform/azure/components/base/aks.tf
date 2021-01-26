## AKS kubernetes cluster ##
resource "azurerm_kubernetes_cluster" "mhs_adaptor_aks" { 
  name                = var.cluster_name
  resource_group_name = azurerm_resource_group.mhs_adaptor.name
  location            = azurerm_resource_group.mhs_adaptor.location
  dns_prefix          = var.dns_prefix
  private_cluster_enabled = false

  linux_profile {
    admin_username = var.admin_username

    ## SSH key is generated using "tls_private_key" resource
    ssh_key {
      key_data = "${trimspace(tls_private_key.key.public_key_openssh)} ${var.admin_username}@azure.com"
    }
  }

  addon_profile {
    http_application_routing {
      enabled = false
    }

    kube_dashboard {
      enabled = false
    }
  }
  
  default_node_pool {
    name = "default"
    node_count = var.agent_count
    vm_size = "Standard_F2s_v2"
    os_disk_size_gb = 30
    vnet_subnet_id = azurerm_subnet.mhs_aks_subnet.id
  }

  network_profile {
    network_plugin = "azure"
    network_policy = "azure"
    service_cidr = var.mhs_aks_internal_cidr
    dns_service_ip = var.mhs_aks_internal_dns
    docker_bridge_cidr = var.mhs_aks_docker_bridge_cidr
    outbound_type      = "userDefinedRouting"
  }

  service_principal {
    client_id     = var.client_id
    client_secret = var.client_secret
  }

  tags = {
    Environment = "Production"
  }

  depends_on = [
    azurerm_subnet.mhs_aks_subnet,
    azurerm_route_table.mhs_aks_route_table,
    azurerm_subnet_route_table_association.mhs_aks_subnet_association
  ]
}

# https://github.com/Azure/AKS/issues/1557
# resource "azurerm_role_assignment" "vmcontributor" {
#   role_definition_name = "Virtual Machine Contributor"
#   scope                = azurerm_resource_group.mhs_adaptor.name
#   principal_id         = azurerm_kubernetes_cluster.mhs_adaptor_aks.identity[0].principal_id
# }

## Outputs ##

# Example attributes available for output
output "id" {
    value = "${azurerm_kubernetes_cluster.mhs_adaptor_aks.id}"
}

output "client_key" {
  value = "${azurerm_kubernetes_cluster.mhs_adaptor_aks.kube_config.0.client_key}"
}

output "client_certificate" {
  value = "${azurerm_kubernetes_cluster.mhs_adaptor_aks.kube_config.0.client_certificate}"
}

output "cluster_ca_certificate" {
  value = "${azurerm_kubernetes_cluster.mhs_adaptor_aks.kube_config.0.cluster_ca_certificate}"
}

output "kube_config" {
  value = azurerm_kubernetes_cluster.mhs_adaptor_aks.kube_config_raw
}

output "host" {
  value = azurerm_kubernetes_cluster.mhs_adaptor_aks.kube_config.0.host
}

output "configure" {
  value = <<CONFIGURE

Run the following commands to configure kubernetes client:

$ terraform output kube_config > ~/.kube/aksconfig
$ export KUBECONFIG=~/.kube/aksconfig

Test configuration using kubectl

$ kubectl get nodes
CONFIGURE
}