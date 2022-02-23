resource "azurerm_postgresql_server" "postgres_server" {
  name                = "${local.resource_prefix}-psqlserver"
  location            = var.location
  resource_group_name = var.account_resource_group

  administrator_login          = var.postgres_master_user
  administrator_login_password = var.postgres_master_password

  sku_name   = var.postgres_sku_name
  version    = "11"
  storage_mb = 20480

  backup_retention_days        = var.backup_retention_period
  geo_redundant_backup_enabled = true
  auto_grow_enabled            = false

  public_network_access_enabled    = false
  ssl_enforcement_enabled          = true
  ssl_minimal_tls_version_enforced = var.ssl_postgres_protocol

tags = merge(local.default_tags,{
Name = "${local.resource_prefix}-postgres-server"
  })
}

resource "azurerm_postgresql_database" "postgres_database" {
  name                = "postgresql"
  resource_group_name = var.account_resource_group
  server_name         = azurerm_postgresql_server.postgres_server.name
  charset             = "UTF8"
  collation           = "English_United Kingdom.1252"
}