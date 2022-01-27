resource "aws_iam_role" "pss_testbox_stop_start_role" {
  count = var.create_testbox_stopstart_role ? 1 : 0
  name = "SSM_StartStop_Pss_testbox_Role"

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


resource "aws_iam_policy" "pss_testbox_stop_start_Policy" {
  count = var.create_testbox_stopstart_role ? 1 : 0
  name        = "SSM_StartStop_PSS_testbox_Policy"
  description = "My test policy"

 
  policy = jsonencode({
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "VisualEditor0",
            "Effect": "Allow",
            "Action": [
                "ec2:StartInstances",
                "ec2:StopInstances"
            ],
            "Resource": "*",
            "Condition": {
                "ForAllValues:StringEquals": {
                    "aws:TagKeys": "Stop-Start-Testbox"
                }
            }
        }
    ]
})
}

resource "aws_iam_role_policy_attachment" "pss_testbox_policy_attach" {
  count = var.create_testbox_stopstart_role ? 1 : 0
  role       = aws_iam_role.pss_testbox_stop_start_role[0].name
  policy_arn = aws_iam_policy.pss_testbox_stop_start_Policy[0].arn
}