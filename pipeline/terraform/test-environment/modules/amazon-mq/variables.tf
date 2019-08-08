variable "environment" {
  type = string
  description = "A name for the environment to be used."
}
variable "security_group_ids" {
  type = list(string)
  description = "The ID of the security group to use."
}