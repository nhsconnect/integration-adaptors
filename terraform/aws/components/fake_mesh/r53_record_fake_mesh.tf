resource "aws_route53_record" "fake_mesh_lb_record" {
  zone_id = data.terraform_remote_state.base.outputs.r53_zone_id
  name = "mesh.${data.terraform_remote_state.base.outputs.r53_zone_name}"
  type = "A"

  alias {
    name    = module.fake_mesh_ecs_service.loadbalancer_dns_name
    zone_id = module.fake_mesh_ecs_service.loadbalancer_zone_id
    evaluate_target_health = false
  }
}
