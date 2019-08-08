provider "aws" {
  profile = var.profile
  region = var.region
}

module "ecs" {
  source = "./modules/ecs"

  region = var.region
  build_id = var.build_id
  cluster_id = var.cluster_id
  ecr_address = var.ecr_address
  mhs_log_level = var.mhs_log_level
  scr_ecr_address = var.scr_ecr_address
  scr_log_level = var.scr_log_level
  scr_service_port = var.scr_service_port
  task_execution_role = var.task_execution_role
  environment = var.environment
}

module "amazon-mq" {
  source = "./modules/amazon-mq"

  environment = var.environment
  security_group_ids = var.queue_security_group_ids
}