data "aws_iam_role" "ecs_service_task_role" {
  name = "MHSTaskRole"
}

# uses the same Task Role as MHS - TODO check what is needed and create separate role for NHAIS
