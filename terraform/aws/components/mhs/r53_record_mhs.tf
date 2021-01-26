resource "aws_route53_record" "mhs_inbound_lb_record" {
  zone_id = data.terraform_remote_state.base.outputs.r53_zone_id
  name = "mhs-inbound.${data.terraform_remote_state.base.outputs.r53_zone_name}"
  type = "A"

  alias {
    name    = module.mhs_inbound_ecs_service.loadbalancer_dns_name
    zone_id = module.mhs_inbound_ecs_service.loadbalancer_zone_id
    evaluate_target_health = false
  }
}

resource "aws_route53_record" "mhs_outbound_lb_record" {
  zone_id = data.terraform_remote_state.base.outputs.r53_zone_id
  name = "mhs-outbound.${data.terraform_remote_state.base.outputs.r53_zone_name}"
  type = "A"

  alias {
    name    = module.mhs_outbound_ecs_service.loadbalancer_dns_name
    zone_id = module.mhs_outbound_ecs_service.loadbalancer_zone_id
    evaluate_target_health = false
  }
}

resource "aws_route53_record" "mhs_route_lb_record" {
  zone_id = data.terraform_remote_state.base.outputs.r53_zone_id
  name = "mhs-route.${data.terraform_remote_state.base.outputs.r53_zone_name}"
  type = "A"

  alias {
    name    = module.mhs_route_ecs_service.loadbalancer_dns_name
    zone_id = module.mhs_route_ecs_service.loadbalancer_zone_id
    evaluate_target_health = false
  }
}
