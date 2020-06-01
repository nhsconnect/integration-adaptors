variable default_tags {
  type = map(string)
  description = "Map of tags to assign to resources in this module"
}

variable "resource_prefix" {
  type = string
  description = "String that will be added as prefix to resource names in this module"
}

variable "module_name" {
  type = string
  description = "(Static) Name of this module"
  default = "ecs_cluster"
}

variable "module_instance" {
  type = string
  description = "(Required) Name of the instance of this module"
}

variable "container_insights" {
  type = string
  default = "disabled"
  description = "(Optional) Container Insights for containers in the cluster, default is disabled"
}