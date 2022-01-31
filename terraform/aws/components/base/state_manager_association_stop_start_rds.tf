resource "aws_ssm_association" "stop_rds_association" {
  count = var.enable_start_stop_scheduler ? 1 : 0
  name = aws_ssm_document.stop_rds_document[0].name
  association_name = "${replace(local.resource_prefix,"_","-")}-Stop-RDS"
  schedule_expression = var.postgres_scheduler_stop_pattern
  

  parameters = { 
    InstanceId = aws_db_instance.base_postgres_db[0].id
    AutomationAssumeRole = data.terraform_remote_state.account.outputs.scheduler_role_arn
  }
}

resource "aws_ssm_document" "stop_rds_document" {
  count = var.enable_start_stop_scheduler ? 1 : 0
  name          = "StopRdsInstance-${replace(local.resource_prefix,"_","-")}"
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
}

resource "aws_ssm_association" "start_rds_association" {
  count = var.enable_start_stop_scheduler ? 1 : 0
  name = aws_ssm_document.start_rds_document[0].name
  association_name = "${replace(local.resource_prefix,"_","-")}-Start-RDS"
  schedule_expression = var.postgres_scheduler_start_pattern
  

  parameters = { 
    InstanceId = aws_db_instance.base_postgres_db[0].id
    AutomationAssumeRole = data.terraform_remote_state.account.outputs.scheduler_role_arn
  }
}

resource "aws_ssm_document" "start_rds_document" {
  count = var.enable_start_stop_scheduler ? 1 : 0
  name          = "StartRdsInstance-${replace(local.resource_prefix,"_","-")}"
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