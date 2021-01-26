# MongoDB on CosmosDB

resource "azurerm_cosmosdb_account" "mongodb" {
  name = "${var.cluster_name}-mongodb"
  resource_group_name = azurerm_resource_group.mhs_adaptor.name
  location            = azurerm_resource_group.mhs_adaptor.location
  offer_type = "Standard"
  kind = "MongoDB"

  enable_automatic_failover = false

  capabilities {
    name = "MongoDBv3.4"
  }

  consistency_policy {
    consistency_level       = "BoundedStaleness"
    max_interval_in_seconds = 10
    max_staleness_prefix    = 200
  }

  geo_location {
    location          = azurerm_resource_group.mhs_adaptor.location
    failover_priority = 0
  }
}

output "mongodb_endpoint" {
  value = azurerm_cosmosdb_account.mongodb.endpoint
}

output "mongodb_write_endpoints" {
  value = azurerm_cosmosdb_account.mongodb.write_endpoints
}

output "mongodb_read_endpoints" {
  value = azurerm_cosmosdb_account.mongodb.read_endpoints
}

output "mongodb_connection_string" {
  value = azurerm_cosmosdb_account.mongodb.connection_strings
}