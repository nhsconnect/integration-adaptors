output "lab-results_url" {
  value = aws_route53_record.lab-results_lb_record.name
  description = "The DNS name of the Route53 record pointing to the LAB-RESULTS service's load balancer."
}

output "lab-results_lb_sg_id" {
  value = module.lab-results_ecs_service.loadbalancer_sg_id
  description = "Security Group ID for LAB-RESULTS load balancer, use it create rules to allow other components to connect"
}
# TODO - In case of chicken and egg situation - cross dependency between components - create SG and rules in base components and supply the SG IDs to components and ECS modules

output "lab-results_lb_port" {
  value = var.lab-results_service_application_port
  description = "Port on which LAB-RESULTS LB is listening"
}

output "lab-results_lb_arn" {
  value =  module.lab-results_ecs_service.loadbalancer_arn
  description = "ARN of Service loadbalancer"
}

output "lab-results_lb_target_group_arn" {
  value =  module.lab-results_ecs_service.loadbalancer_tg_arn
  description = "ARN of Service loadbalancers target group"
}

output "lab-results_external_access_sg_id" {
  value = aws_security_group.lab-results_external_access.id
  description = "ID of the security group allowing LAB-RESULTS to call other services"
}

output "lab-results_service_subnets" {
  value = aws_subnet.service_subnet.*.id
  description = "Subnets used by LAB-RESULTS service"
}
