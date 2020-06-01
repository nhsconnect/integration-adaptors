output "loadbalancer_sg_id" {
  value =  var.enable_load_balancing ? aws_security_group.service_lb_sg.id : null
}

output "loadbalancer_dns_name" {
  value =  var.enable_load_balancing ? aws_lb.service_load_balancer[0].dns_name : null
}

output "loadbalancer_zone_id" {
  value =  var.enable_load_balancing ? aws_lb.service_load_balancer[0].zone_id : null
}
