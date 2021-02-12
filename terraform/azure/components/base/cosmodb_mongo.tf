resource "azurerm_cosmosdb_account" "mongodb" {
  name = "${local.resource_prefix}-mongodb"
  resource_group_name = var.account_resource_group
  location            = var.location
  offer_type          = "Standard"
  kind                = "MongoDB"

  enable_automatic_failover = false

  capabilities {
    name = "EnableMongo"
  }

  capabilities {
    name = "MongoDBv3.4"
  }

  consistency_policy {
    consistency_level       = "BoundedStaleness"
    max_interval_in_seconds = 10
    max_staleness_prefix    = 200
  }

  geo_location {
    location          = var.location
    failover_priority = 0
  }

  tags = merge(local.default_tags,{
    Name = "${local.resource_prefix}-mongodb"
  })
}
