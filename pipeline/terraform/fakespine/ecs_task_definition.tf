# Fake Spine ECS task definition
resource "aws_ecs_task_definition" "fake_spine_task" {
  family = "${var.environment_id}-fake-spine"
  container_definitions = jsonencode(
  [
    {
      name = "fake-spine"
      //image = "${var.ecr_address}/fake-spine:${var.build_id}"
      image = "067756640211.dkr.ecr.eu-west-2.amazonaws.com/fake-spine:PR-188-113-702c9e9" // use the same image - no need to rebuild it
      environment = [{
        name = "INBOUND_SERVER_BASE_URL",
        value = var.inbound_server_base_url
      }, {
        name = "FAKE_SPINE_OUTBOUND_DELAY_MS",
        value = var.outbound_delay_ms
      }, {
        name = "FAKE_SPINE_INBOUND_DELAY_MS",
        value = var.inbound_delay_ms
      }, {
        name = "FAKE_SPINE_OUTBOUND_SSL_ENABLED"
        value = var.fake_spine_outbound_ssl
      }, {
        name = "FAKE_SPINE_PORT"
        value = var.fake_spine_port
      }]
      secrets = [{
        name = "FAKE_SPINE_PRIVATE_KEY",
        valueFrom = var.fake_spine_private_key
      }, {
        name = "FAKE_SPINE_CERTIFICATE",
        valueFrom = var.fake_spine_certificate
      }, {
        name = "FAKE_SPINE_CA_STORE",
        valueFrom = var.fake_spine_ca_store
      }, {
        name = "MHS_SECRET_PARTY_KEY",
        valueFrom = var.party_key_arn
      }]
      essential = true
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          awslogs-group = aws_cloudwatch_log_group.fake_spine_log_group.name
          awslogs-region = var.region
          awslogs-stream-prefix = var.build_id
          awslogs-datetime-format = "\\[%Y-%m-%dT%H:%M:%S\\.%fZ\\]"
        }
      }
      portMappings = [
        {
          containerPort = tonumber(var.fake_spine_port)
          hostPort = tonumber(var.fake_spine_port)
          protocol = "tcp"
        }
      ]
    }
  ]
  )
  cpu = "512"
  memory = "1024"
  network_mode = "awsvpc"
  requires_compatibilities = [
    "FARGATE"
  ]
  tags = {
    Name = "${var.environment_id}-fake-spine-task"
    EnvironmentId = var.environment_id
  }
  task_role_arn = var.task_role_arn
  execution_role_arn = var.execution_role_arn
}
