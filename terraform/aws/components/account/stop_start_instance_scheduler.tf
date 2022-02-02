resource "aws_iam_role" "enable_stop_start_scheduler_role" {
  //count = var.create_testbox_stopstart_role ? 1 : 0
  name = "Enable-Stop-Start-Scheduler-Role"

  assume_role_policy = jsonencode({
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "ec2.amazonaws.com",
        "Service": "ssm.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
})
}


resource "aws_iam_policy" "enable_stop_start_scheduler_policy" {
  //count = var.create_testbox_stopstart_role ? 1 : 0
  name        = "Enable-Stop-Start-Scheduler-Policy"
  description = "Enable Stop Start Scheduler"

 
  policy = jsonencode({
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "VisualEditor0",
            "Effect": "Allow",
            "Action": [
                "ec2:StartInstances",
                "ec2:StopInstances",
                "ec2:DescribeInstances",
                "ec2:RebootInstances",
                "ec2:DescribeInstanceStatus",
                "rds:Describe*",
                "rds:Start*",
                "rds:Stop*",
                "rds:Reboot*"
            ],
            "Resource": "*",
            "Condition": {
                "ForAllValues:StringEquals": {
                    "aws:TagKeys": "EnableScheduler"
                }
            }
        }
    ]
})
}

resource "aws_iam_role_policy_attachment" "enable_stop_start_scheduler_policy_attach" {
  //count = var.create_testbox_stopstart_role ? 1 : 0
  role       = aws_iam_role.enable_stop_start_scheduler_role.name
  policy_arn = aws_iam_policy.enable_stop_start_scheduler_policy.arn
}