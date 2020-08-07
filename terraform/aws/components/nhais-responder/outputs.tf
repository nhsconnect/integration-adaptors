output "nhais_responder_url" {
  value = aws_route53_record.nhais_responder_lb_record.name
  description = "The DNS name of the Route53 record pointing to the nhais_responder service's load balancer."
}

output "nhais_lb_sg_id" {
  value = module.nhais_responder_ecs_service.loadbalancer_sg_id
  description = "Security Group ID for NHAIS_Responder load balancer, use it create rules to allow other components to connect"
}
# TODO - In case of chicken and egg situation - cross dependency between components - create SG and rules in base components and supply the SG IDs to components and ECS modules

output "nhais_responder_lb_port" {
  value = var.nhais_responder_service_application_port
  description = "Port on which nhais_responder LB is listening"
}

output "nhais_responder_lb_arn" {
  value =  module.nhais_responder_ecs_service.loadbalancer_arn
  description = "ARN of Service loadbalancer"
}

output "nhais_responder_lb_target_group_arn" {
  value =  module.nhais_responder_ecs_service.loadbalancer_tg_arn
  description = "ARN of Service loadbalancers target group"
}

output "nhais_responder_external_access_sg_id" {
  value = aws_security_group.nhais_responder_external_access.id
  description = "ID of the security group allowing nhais_responder to call other services"
}
