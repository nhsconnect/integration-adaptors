locals {
  environment_variables = concat(var.gp2gp_environment_variables,[
    {
      name = "LOG_LEVEL"
      value = var.gp2gp_log_level
    }
  ])
}
