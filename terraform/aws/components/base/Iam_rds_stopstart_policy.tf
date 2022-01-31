/*resource "aws_iam_role" "rds_stop_start_role" {
  count = var.create_rds_stopstart_role ? 1 : 0
  name = "${replace(local.resource_prefix,"_","-")}-rds-scheduler"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ssm.amazonaws.com"
        }
      },
    ]
  })
}


resource "aws_iam_policy" "rds_stop_start_Policy" {
  count = var.create_rds_stopstart_role ? 1 : 0
  name        = "${replace(local.resource_prefix,"_","-")}-rds-auto-stopstart"
  description = "My test policy"

 
  policy = jsonencode({
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "rds:Describe*",
                "rds:Start*",
                "rds:Stop*",
                "rds:Reboot*"
            ],
            "Resource": "*",
            "Condition": {
                "ForAllValues:StringEqualsIfExists": {
                    "aws:TagKeys": "AutoStopStart"
                }
             }
        }
    ]
})
}

resource "aws_iam_role_policy_attachment" "rds_policy_attach" {
  count = var.create_rds_stopstart_role ? 1 : 0
  role       = aws_iam_role.rds_stop_start_role[0].name
  policy_arn = aws_iam_policy.rds_stop_start_Policy[0].arn
}*/