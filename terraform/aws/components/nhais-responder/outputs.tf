output "nhais-responder_url" {
  value = aws_route53_record.nhais-responder_lb_record.name
  description = "The DNS name of the Route53 record pointing to the NHAIS-Responder service's load balancer."
}

output "nhais_lb_sg_id" {
  value = module.nhais-responder_ecs_service.loadbalancer_sg_id
  description = "Security Group ID for NHAIS-Respomder load balancer, use it create rules to allow other components to connect"
}
# TODO - In case of chicken and egg situation - cross dependency between components - create SG and rules in base components and supply the SG IDs to components and ECS modules

output "nhais-responder_lb_port" {
  value = var.nhais-responder_service_application_port
  description = "Port on which NHAIS-Responder LB is listening"
}

output "nhais-responder_lb_arn" {
  value =  module.nhais-responder_ecs_service.loadbalancer_arn
  description = "ARN of Service loadbalancer"
}

output "nhais-responder_lb_target_group_arn" {
  value =  module.nhais-responder_ecs_service.loadbalancer_tg_arn
  description = "ARN of Service loadbalancers target group"
}

output "nhais-responder_external_access_sg_id" {
  value = aws_security_group.nhais-responder_external_access.id
  description = "ID of the security group allowing NHAIS-Responder to call other services"
}
