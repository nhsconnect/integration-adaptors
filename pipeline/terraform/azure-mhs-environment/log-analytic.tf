resource "random_id" "log_analytics_workspace_name_suffix" {
    byte_length = 8
}

resource "azurerm_log_analytics_workspace" "k8-logs" {
    # The WorkSpace name has to be unique across the whole of azure, not just the current subscription/tenant.
    name                = "${var.cluster_name}-${random_id.log_analytics_workspace_name_suffix.dec}"
    location            = azurerm_resource_group.mhs_adaptor.location
    resource_group_name = azurerm_resource_group.mhs_adaptor.name
    sku                 = "PerGB2018"
    retention_in_days   = 30
}

resource "azurerm_log_analytics_solution" "log-analytics" {
    solution_name         = "ContainerInsights"
    location              = azurerm_resource_group.mhs_adaptor.location
    resource_group_name   = azurerm_resource_group.mhs_adaptor.name
    workspace_resource_id = azurerm_log_analytics_workspace.k8-logs.id
    workspace_name        = azurerm_log_analytics_workspace.k8-logs.name

    plan {
        publisher = "Microsoft"
        product   = "OMSGallery/ContainerInsights"
    }
}