## Azure resource group for the kubernetes cluster ##
resource "azurerm_resource_group" "nia_base" {
  name     = var.resource_group_name
  location = var.location
}

output "resource_group_name" {
  value = azurerm_resource_group.nia_base.name
}

output resource_group_location {
  value = azurerm_resource_group.nia_base.location
}
