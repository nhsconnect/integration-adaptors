variable "environment" {
  type = string
  description = "A name for the environment to be used."
}
variable "security_group_id" {
  type = string
  description = "The ID of the security group to use."
}
variable "queue_user" {
  type = string
  description = "The username for the default user to use."
}
variable "queue_pass" {
  type = string
  description = "The password for the default user to use."
}