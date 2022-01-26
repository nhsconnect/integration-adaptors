/*resource "aws_ssm_association" "stop_rds_association" {
  count = var.postgresdb_scheduler_enabled ? 1 : 0
  name = aws_ssm_document.stop_rds_document.name
  association_name = "{replace(local.resource_prefix,"_","-")}-Stop_RDS"
  schedule_expression = var.postgresdb_scheduler_stop_pattern
  

  parameters = { 
    InstanceId = aws_db_instance.base_postgres_db[0].id
    AutomationAssumeRole = data.terraform_remote_state.account.outputs.rds_iam_role
  }
}

resource "aws_ssm_document" "stop_rds_document" {
  name          = "StopRdsInstance"
  document_format = "YAML"
  document_type = "Automation"

  content = <<DOC
description: Stop RDS instance
schemaVersion: '0.3'
assumeRole: '{{ AutomationAssumeRole }}'
parameters:
  InstanceId:
    type: String
    description: (Required) RDS Instance Id to stop
  AutomationAssumeRole:
    type: String
    description: >-
      (Optional) The ARN of the role that allows Automation to perform the
      actions on your behalf.
    default: ''
mainSteps:
  - name: AssertNotStopped
    action: 'aws:assertAwsResourceProperty'
    isCritical: false
    onFailure: 'step:StopInstance'
    nextStep: CheckStop
    inputs:
      Service: rds
      Api: DescribeDBInstances
      DBInstanceIdentifier: '{{InstanceId}}'
      PropertySelector: '$.DBInstances[0].DBInstanceStatus'
      DesiredValues:
        - stopped
        - stopping
  - name: StopInstance
    action: 'aws:executeAwsApi'
    inputs:
      Service: rds
      Api: StopDBInstance
      DBInstanceIdentifier: '{{InstanceId}}'
  - name: CheckStop
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
        - stopped
DOC
}*/