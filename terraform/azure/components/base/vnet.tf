resource "azurerm_virtual_network" "nia_vnet" {
  name                = "nia_vnet"
  resource_group_name = azurerm_resource_group.nia_base.name
  location            = azurerm_resource_group.nia_base.location
  address_space       = [var.nia_vnet_cidr]

  tags = {
    environment = "Production"
  }
}

resource "azurerm_subnet" "nia_jumpbox_subnet" {
  name = "nia_jumpbox_subnet"
  resource_group_name = azurerm_resource_group.nia_base.name
  virtual_network_name = azurerm_virtual_network.nia_vnet.name
  address_prefixes    = [var.jumpbox_subnet_cidr]

  service_endpoints = [
    "Microsoft.AzureCosmosDB",
    "Microsoft.ContainerRegistry",
    "Microsoft.ServiceBus",
    "Microsoft.Storage"
  ]
}

data "azurerm_virtual_network" "mhs_vnet" {
  name = "mhs_vnet"
  resource_group_name = data.azurerm_resource_group.mhs_rg.name
}

data "azurerm_resource_group" "mhs_rg" {
  name = "mhs-rg"
}

resource "azurerm_virtual_network_peering" "peering-base-to-mhs" {
  name                      = "peering_base_to_mhs"
  resource_group_name       = azurerm_resource_group.nia_base.name
  virtual_network_name      = azurerm_virtual_network.nia_vnet.name
  remote_virtual_network_id = data.azurerm_virtual_network.mhs_vnet.id
}

resource "azurerm_virtual_network_peering" "peering-mhs-to-base" {
  name                      = "peering_mhs_to_base"
  resource_group_name       = data.azurerm_resource_group.mhs_rg.name
  virtual_network_name      = data.azurerm_virtual_network.mhs_vnet.name
  remote_virtual_network_id = azurerm_virtual_network.nia_vnet.id
}