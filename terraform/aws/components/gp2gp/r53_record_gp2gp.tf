resource "aws_route53_record" "gp2gp_lb_record" {
  zone_id = data.terraform_remote_state.base.outputs.r53_zone_id
  name = "gp2gp.${data.terraform_remote_state.base.outputs.r53_zone_name}"
  type = "A"

  alias {
    name    = module.gp2gp_ecs_service.loadbalancer_dns_name
    zone_id = module.gp2gp_ecs_service.loadbalancer_zone_id
    evaluate_target_health = false
  }
}
