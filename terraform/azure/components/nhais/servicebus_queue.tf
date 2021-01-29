resource "azurerm_servicebus_queue" "nhais_mesh_inbound_queue" {
  name                = "${local.resource_prefix}-mesh_inbound_queue"
  resource_group_name = var.account_resource_group
  namespace_name      = data.terraform_remote_state.base.outputs.base_servicebus_namespace

  enable_partitioning = false
}

resource "azurerm_servicebus_queue" "nhais_mesh_outbound_queue" {
  name                = "${local.resource_prefix}-mesh-outbound-queue"
  resource_group_name = var.account_resource_group
  namespace_name      = data.terraform_remote_state.base.outputs.base_servicebus_namespace

  enable_partitioning = false
}

resource "azurerm_servicebus_queue" "nhais_gp_inbound_queue" {
  name                = "${local.resource_prefix}-gp-inbound-queue"
  resource_group_name = var.account_resource_group
  namespace_name      = data.terraform_remote_state.base.outputs.base_servicebus_namespace

  enable_partitioning = false
}

resource "azurerm_servicebus_queue_authorization_rule" "nhais_mesh_inbound_queue_ar" {
  name = "${local.resource_prefix}-mesh_inbound_queue_ar"
  resource_group_name = var.account_resource_group
  namespace_name = data.terraform_remote_state.base.outputs.base_servicebus_namespace
  queue_name = azurerm_servicebus_queue.nhais_mesh_inbound_queue.name

  listen = true
  send = true
  manage = false
}

resource "azurerm_servicebus_queue_authorization_rule" "nhais_mesh_outbound_queue_ar" {
  name = "${local.resource_prefix}-mesh_outbound_queue_ar"
  resource_group_name = var.account_resource_group
  namespace_name = data.terraform_remote_state.base.outputs.base_servicebus_namespace
  queue_name = azurerm_servicebus_queue.nhais_mesh_outbound_queue.name

  listen = true
  send = true
  manage = false
}

resource "azurerm_servicebus_queue_authorization_rule" "nhais_gp_inbound_queue_ar" {
  name = "${local.resource_prefix}-gp_inbound_queue_ar"
  resource_group_name = var.account_resource_group
  namespace_name = data.terraform_remote_state.base.outputs.base_servicebus_namespace
  queue_name = azurerm_servicebus_queue.nhais_gp_inbound_queue.name

  listen = true
  send = true
  manage = false
}

#

output nhais_mesh_inbound_queue_name {
  value = azurerm_servicebus_queue.nhais_mesh_inbound_queue.name
}

output nhais_mesh_outbound_queue_name {
  value = azurerm_servicebus_queue.nhais_mesh_outbound_queue.name
}

output nhais_gp_inbound_queue_name {
  value = azurerm_servicebus_queue.nhais_gp_inbound_queue.name
}

#

output nhais_mesh_inbound_queue_username {
  value = azurerm_servicebus_queue_authorization_rule.nhais_mesh_inbound_queue_ar.name
}

output nhais_mesh_outbound_queue_username {
  value = azurerm_servicebus_queue_authorization_rule.nhais_mesh_outbound_queue_ar.name
}

output nhais_gp_inbound_queue_username {
  value = azurerm_servicebus_queue_authorization_rule.nhais_gp_inbound_queue_ar.name
}



# output "inbound_service_bus_host" {
#   description = "Hostname for Service Bus endpoint"
#   value = replace(replace(split(";", azurerm_servicebus_queue_authorization_rule.mhs_inbound_queue_ar.primary_connection_string)[0],"Endpoint=sb://",""),"/","")
# }

# output "inbound_service_bus_port" {
#   value = "5671"
# }

# output "inbound_service_bus_queue_name" {
#   value = azurerm_servicebus_queue.mhs_inbound_queue.name
# }

# output "inbound_service_bus_queue_username" {
#    value = azurerm_servicebus_queue_authorization_rule.mhs_inbound_queue_ar.name
# }

# output "inbound_service_bus_connection_string" {
#   description = "Primary connection string for Service Bus Namespace"
#   value = azurerm_servicebus_namespace.mhs_inbound_servicebus_namespace.default_primary_connection_string
# }

# output "inbound_service_bus_primary_key" {
#   description = "Primary key for Service Bus Namespace"
#   value = azurerm_servicebus_namespace.mhs_inbound_servicebus_namespace.default_primary_key
# }

# output "inbound_queue_ar_primary_key" {
#   value = azurerm_servicebus_queue_authorization_rule.mhs_inbound_queue_ar.primary_key
# }

# output "inbound_queue_ar_primary_connection_string" {
#   value = azurerm_servicebus_queue_authorization_rule.mhs_inbound_queue_ar.primary_connection_string
# }

# output "outbound_queue_ar_primary_key" {
#   value = azurerm_servicebus_queue_authorization_rule.mhs_outbound_queue_ar.primary_key
# }

# output "outbound_queue_ar_primary_connection_string" {
#   value = azurerm_servicebus_queue_authorization_rule.mhs_outbound_queue_ar.primary_connection_string
# }