resource "aws_route53_record" "OneOneOne_lb_record" {
  zone_id = data.terraform_remote_state.base.outputs.r53_zone_id
  name = "111.${data.terraform_remote_state.base.outputs.r53_zone_name}"
  type = "A"

  alias {
    name    = module.OneOneOne_ecs_service.loadbalancer_dns_name
    zone_id = module.OneOneOne_ecs_service.loadbalancer_zone_id
    evaluate_target_health = false
  }
}
