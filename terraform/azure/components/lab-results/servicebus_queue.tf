resource "azurerm_servicebus_queue" "lab-results_mesh_inbound_queue" {
  name                = "${local.resource_prefix}-mesh_inbound_queue"
  resource_group_name = var.account_resource_group
  namespace_name      = data.terraform_remote_state.base.outputs.base_servicebus_namespace

  enable_partitioning = false
}

resource "azurerm_servicebus_queue" "lab-results_mesh_outbound_queue" {
  name                = "${local.resource_prefix}-mesh-outbound-queue"
  resource_group_name = var.account_resource_group
  namespace_name      = data.terraform_remote_state.base.outputs.base_servicebus_namespace

  enable_partitioning = false
}

resource "azurerm_servicebus_queue" "lab-results_gp_outbound_queue" {
  name                = "${local.resource_prefix}-gp-outbound-queue"
  resource_group_name = var.account_resource_group
  namespace_name      = data.terraform_remote_state.base.outputs.base_servicebus_namespace

  enable_partitioning = false
}

# Namespace authorisation rule for all queues

resource "azurerm_servicebus_namespace_authorization_rule" "lab-results_servicebus_ar" {
  name = "${local.resource_prefix}-servicebus_ar"
  resource_group_name = var.account_resource_group
  namespace_name = data.terraform_remote_state.base.outputs.base_servicebus_namespace

  listen = true
  send = true
  manage = false
}
