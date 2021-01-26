resource "azurerm_virtual_network" "mhs_vnet" {
  name                = "mhs_vnet"
  resource_group_name = azurerm_resource_group.mhs_adaptor.name
  location            = azurerm_resource_group.mhs_adaptor.location
  address_space       = [var.mhs_vnet_cidr]
  #dns_servers         = var.dns_servers

  ddos_protection_plan {
    id     = azurerm_network_ddos_protection_plan.mhs_ddos_plan.id
    enable = false
  }

  tags = {
    environment = "Production"
  }
}

resource "azurerm_network_ddos_protection_plan" "mhs_ddos_plan" {
  name                = "mhs_ddos_plan"
  resource_group_name = azurerm_resource_group.mhs_adaptor.name
  location            = azurerm_resource_group.mhs_adaptor.location
}
