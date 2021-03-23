resource "aws_iam_role" "ecs_service_task_execution_role" {
  name = "${local.resource_prefix}-task_execution_role"
  assume_role_policy = data.aws_iam_policy_document.ecs_service_task_execution_assume_role.json
}

resource "aws_iam_role_policy_attachment" "ecs_service_task_execution_role_aws_attachment" {
  role = aws_iam_role.ecs_service_task_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

resource "aws_iam_role_policy_attachment" "ecs_service_task_execution_role_s3_attachment" {
  role = aws_iam_role.ecs_service_task_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess"
}

resource "aws_iam_role_policy_attachment" "ecs_service_task_execution_role_sm_attachment" {
  role = aws_iam_role.ecs_service_task_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/SecretsManagerReadWrite"
}

resource "aws_iam_role_policy_attachment" "ecs_service_task_execution_policies_attachment" { 
  role = aws_iam_role.ecs_service_task_execution_role.name
  policy_arn = aws_iam_policy.ecs_service_task_execution_role_policy.arn
}

resource "aws_iam_policy" "ecs_service_task_execution_role_policy" {
  name = "${local.resource_prefix}-iam-task-execution-policy"
  description = "Policy for ECS tasks running NHAIS in env: ${var.environment}"
  policy = data.aws_iam_policy_document.ecs_service_task_execution_policies.json
}

data "aws_iam_policy_document" "ecs_service_task_execution_assume_role" {
  statement {
    actions = ["sts:AssumeRole"]
    effect = "Allow"
    principals {
      type = "Service"
      identifiers = ["ecs-tasks.amazonaws.com"]
    }
  }
}

data "aws_iam_policy_document" "ecs_service_task_execution_policies" {

  statement {
    effect = "Allow"
    actions = [
      "kms:Decrypt",
      "secretsmanager:GetSecretValue"
    ]
    resources = [
      "arn:aws:secretsmanager:${var.region}:${var.account_id}:secret:*",
      "arn:aws:kms:${var.region}:${var.account_id}:key/*"
    ]
  }

  statement {
    effect = "Allow"
    actions = [
      "ecr:GetAuthorizationToken",
      "logs:CreateLogGroup",
      "logs:CreateLogStream",
      "logs:PutLogEvents",
      "logs:DescribeLogGroups",
      "logs:DescribeLogStreams",
    ]
    resources = ["*"]
  }

  statement {
    effect = "Allow"
    actions = [
      "ecr:BatchGetImage",
      "ecr:GetDownloadUrlForLayer",
      "ecr:BatchCheckLayerAvailability",
      "ecr:ListImages",
      "ecr:DescribeRepositories",
      "ecr:DescribeImages",
      "ecr:DescribeImageScanFindings",
      "ecr:GetLifecyclePolicy",
      "ecr:GetLifecyclePolicyPreview",
      "ecr:GetRepositoryPolicy",
      "ecr:ListTagsForResource",
    ]

    resources = ["*"]
  }
}

data "aws_iam_role" "mhs_task_execution_role" {
  name = "BuildMHS-ECSTaskExecutionRole"
}

