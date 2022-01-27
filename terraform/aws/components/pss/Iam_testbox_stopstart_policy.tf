resource "aws_iam_role" "pss_testbox_stop_start_role" {
  count = var.create_testbox_stopstart_role ? 1 : 0
  name = "${replace(local.resource_prefix,"_","-")}-StartStop-Pss-Testbox-Role"

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


resource "aws_iam_policy" "pss_testbox_stop_start_Policy" {
  count = var.create_testbox_stopstart_role ? 1 : 0
  name        = "${replace(local.resource_prefix,"_","-")}-StartStop-PSS-Testbox-Policy"
  description = "My test policy"

 
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
                "ec2:DescribeInstanceStatus"
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