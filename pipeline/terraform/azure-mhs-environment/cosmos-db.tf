resource "azurerm_cosmosdb_account" "mhs_state_table" {
  name                = "${var.cluster_name}-mhs-state"
  location            = azurerm_resource_group.mhs_adaptor.location
  resource_group_name = azurerm_resource_group.mhs_adaptor.name
  offer_type          = "Standard"
  kind                = "GlobalDocumentDB"

  consistency_policy {
    consistency_level       = "BoundedStaleness"
    max_interval_in_seconds = 10
    max_staleness_prefix    = 200
  }

  geo_location {
    prefix            = "${var.cluster_name}-mhs-state"
    location          = azurerm_resource_group.mhs_adaptor.location
    failover_priority = 0
  }
}
resource "azurerm_cosmosdb_account" "mhs_sync_async_table" {
  name                = "${var.cluster_name}-mhs-sync-async-state"
  location            = azurerm_resource_group.mhs_adaptor.location
  resource_group_name = azurerm_resource_group.mhs_adaptor.name
  offer_type          = "Standard"
  kind                = "GlobalDocumentDB"

  consistency_policy {
    consistency_level       = "BoundedStaleness"
    max_interval_in_seconds = 10
    max_staleness_prefix    = 200
  }

  geo_location {
    prefix            = "${var.cluster_name}-mhs-sync-async-state"
    location          = azurerm_resource_group.mhs_adaptor.location
    failover_priority = 0
  }
}