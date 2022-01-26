resource "aws_ssm_association" "start_rds_association" {
  count = var.postgresdb_scheduler_enabled ? 1 : 0
  name = aws_ssm_document.start_rds_document.name
  association_name = "Start_RDS"
  schedule_expression = var.postgresdb_scheduler_start_pattern
  

  parameters = { 
    InstanceId = aws_db_instance.base_postgres_db[0].id
    AutomationAssumeRole = aws_iam_role.rds_stop_start_role.arn
  }
}

resource "aws_ssm_document" "start_rds_document" {
  name          = "StartRdsInstance"
  document_format = "YAML"
  document_type = "Automation"

  content = <<DOC
description: Start RDS instance
schemaVersion: '0.3'
assumeRole: '{{ AutomationAssumeRole }}'
parameters:
  InstanceId:
    type: String
    description: (Required) RDS Instance Id to start
  AutomationAssumeRole:
    type: String
    description: >-
      (Optional) The ARN of the role that allows Automation to perform the
      actions on your behalf.
    default: ''
mainSteps:
  - name: AssertNotStartingOrAvailable
    action: 'aws:assertAwsResourceProperty'
    isCritical: false
    onFailure: 'step:StartInstance'
    nextStep: CheckStart
    inputs:
      Service: rds
      Api: DescribeDBInstances
      DBInstanceIdentifier: '{{InstanceId}}'
      PropertySelector: '$.DBInstances[0].DBInstanceStatus'
      DesiredValues:
        - available
        - starting
  - name: StartInstance
    action: 'aws:executeAwsApi'
    inputs:
      Service: rds
      Api: StartDBInstance
      DBInstanceIdentifier: '{{InstanceId}}'
  - name: CheckStart
    action: 'aws:waitForAwsResourceProperty'
    onFailure: Abort
    maxAttempts: 10
    timeoutSeconds: 600
    inputs:
      Service: rds
      Api: DescribeDBInstances
      DBInstanceIdentifier: '{{InstanceId}}'
      PropertySelector: '$.DBInstances[0].DBInstanceStatus'
      DesiredValues:
        - available
    isEnd: true
DOC
}