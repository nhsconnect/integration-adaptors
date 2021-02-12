resource "azurerm_resource_group" "account_resource_group" {
  name     = var.account_resource_group
  location = var.location

  tags = {
    Name = var.account_resource_group
    Project = var.project
  }
}
