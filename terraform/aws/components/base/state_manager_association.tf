resource "aws_ssm_association" "stop_rds_association" {
  name = aws_ssm_document.stop_rds_document.name
  association_name = "Stop_RDS"
  schedule_expression = "cron(0 00 18 ? * * *)"

  parameters { 
    InstanceId = aws_db_instance.base_postgres_db.id
    AutomationAssumeRole = aws_iam_role.rds_stop_start_role.name
  }
}

resource "aws_ssm_document" "stop_rds_document" {
  name          = "AWS-StopRdsInstance"
  document_type = "Automation"

  content = <<DOC
  {
schemaVersion: "0.3"
assumeRole: "{{ AutomationAssumeRole }}"
parameters:
  InstanceId:
    type: String
    description: (Required) RDS Instance Id to stop
  AutomationAssumeRole:
    type: String
    description: (Optional) The ARN of the role that allows Automation to perform the actions on your behalf.
    default: ""
mainSteps:
  -
    name: AssertNotStopped
    action: aws:assertAwsResourceProperty
    isCritical: false
    onFailure: step:StopInstance
    nextStep: CheckStop
    inputs:
      Service: rds
      Api: DescribeDBInstances
      DBInstanceIdentifier: "{{InstanceId}}"
      PropertySelector: "$.DBInstances[0].DBInstanceStatus"
      DesiredValues: ["stopped", "stopping"]
  -
    name: StopInstance
    action: aws:executeAwsApi
    inputs:
      Service: rds
      Api: StopDBInstance
      DBInstanceIdentifier: "{{InstanceId}}"
  -
    name: CheckStop
    action: aws:waitForAwsResourceProperty
    onFailure: Abort
    maxAttempts: 10
    timeoutSeconds: 600
    inputs:
      Service: rds
      Api: DescribeDBInstances
      DBInstanceIdentifier: "{{InstanceId}}"
      PropertySelector: "$.DBInstances[0].DBInstanceStatus"
      DesiredValues: ["stopped"]
  }
DOC
}