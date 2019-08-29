variable "region" {
  type = string
  default = "eu-west-2"
  description = "The AWS region to deploy to."
}

variable "build_id" {
  type = string
  description = "ID used to identify the current build."
}
