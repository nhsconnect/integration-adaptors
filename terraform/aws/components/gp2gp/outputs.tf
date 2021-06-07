# place for outputs from component

output "gp2gp_service_sg_id" {
  value = module.gp2gp_ecs_service.service_sg_id
  description = "ID of the security group allowing GP2GP to call other services"
}
