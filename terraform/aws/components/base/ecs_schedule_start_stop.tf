resource "null_resource" "schedule_ecs_stop" {

  provisioner "local-exec" {
    command = <<COMMAND
        aws application-autoscaling put-scheduled-action --service-namespace ecs \
        --scalable-dimension ecs:service:DesiredCount \
        --resource-id service/nia-kdev-base-ecs_cluster/nia-kdev-ps_gpc_fcde_ecs-service \
        --scheduled-action-name cron-scaleout-action \
        --schedule "cron(25 18 * * ? *)" \
        --scalable-target-action MinCapacity=0,MaxCapacity=0 \
        --region eu-west-2
COMMAND
  }
}

resource "null_resource" "schedule_ecs_start" {

  provisioner "local-exec" {
    command = <<COMMAND
        aws application-autoscaling put-scheduled-action --service-namespace ecs \
        --scalable-dimension ecs:service:DesiredCount \
        --resource-id service/nia-kdev-base-ecs_cluster/nia-kdev-ps_gpc_fcde_ecs-service \
        --scheduled-action-name cron-scaleout-action \
        --schedule "cron(00 06 * * ? *)" \
        --scalable-target-action MinCapacity=1,MaxCapacity=1 \
        --region eu-west-2
COMMAND
  }
}