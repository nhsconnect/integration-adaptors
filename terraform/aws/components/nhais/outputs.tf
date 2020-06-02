output "nhais_url" {
  value = aws_route53_record.nhais_lb_record.name
  description = "The DNS name of the Route53 record pointing to the NHAIS service's load balancer."
}

output "nhais_lb_sg_id" {
  value = module.nhais_ecs_service.loadbalancer_sg_id
  description = "Security Group ID for NHAIS load balancer, use it create rules to allow other components to connect"
}
# TODO - In case of chicken and egg situation - cross dependency between components - create SG and rules in base components and supply the SG IDs to componnets and ECS modules

output "nhais_lb_port" {
  value = var.nhais_service_application_port
  description = "Port on which NHAIS LB is listening"
}
