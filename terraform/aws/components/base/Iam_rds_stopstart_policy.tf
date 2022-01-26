resource "aws_iam_role" "rds_stop_start_role" {
  name = "rds_scheduler"

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
  name        = "RDS_AutoStopStart"
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
  role       = aws_iam_role.rds_stop_start_role.name
  policy_arn = aws_iam_policy.rds_stop_start_Policy.arn
}