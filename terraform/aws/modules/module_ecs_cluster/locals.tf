locals {
  resource_prefix = "${var.resource_prefix}-${var.module_instance}"
  default_tags = merge(var.default_tags,{
    Module          = var.module_name,
    Module_Instance = var.module_instance,
  })
}