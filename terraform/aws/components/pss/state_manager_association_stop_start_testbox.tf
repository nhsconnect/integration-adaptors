resource "aws_ssm_association" "stop_pss_testbox_association" {
  count = var.pss_testbox_scheduler_enabled ? 1 : 0
  name = aws_ssm_document.stop_pss_testbox_document.name
  association_name = "${replace(local.resource_prefix,"_","-")}-Stop_pss_testbox"
  schedule_expression = var.pss_testbox_scheduler_stop_pattern
  

  parameters = { 
    InstanceId = aws_instance.pss_testbox[0].id
    AutomationAssumeRole = aws_iam_role.pss_testbox_stop_start_role[0].arn
  }
}

resource "aws_ssm_document" "stop_pss_testbox_document" {
  count = var.pss_testbox_scheduler_enabled ? 1 : 0
  name          = "Stop_PSS_Testbox"
  document_type = "Automation"

  content = <<DOC
{
  "description": "Stop EC2 instances(s)",
  "schemaVersion": "0.3",
  "assumeRole": "{{ AutomationAssumeRole }}",
  "parameters": {
    "InstanceId": {
      "type": "StringList",
      "description": "(Required) EC2 Instance(s) to stop"
    },
    "AutomationAssumeRole": {
      "type": "String",
      "description": "(Optional) The ARN of the role that allows Automation to perform the actions on your behalf.",
      "default": ""
    }
  },
  "mainSteps": [
    {
      "name": "stopInstances",
      "action": "aws:changeInstanceState",
      "onFailure": "Continue",
      "inputs": {
        "InstanceIds": "{{ InstanceId }}",
        "DesiredState": "stopped"
      }
    },
    {
      "name": "forceStopInstances",
      "action": "aws:changeInstanceState",
      "inputs": {
        "InstanceIds": "{{ InstanceId }}",
        "CheckStateOnly": false,
        "DesiredState": "stopped",
        "Force": true
      }
    }
  ]
}
DOC
}

/*resource "aws_ssm_association" "start_pss_testbox_association" {
  count = var.pss_testbox_scheduler_enabled ? 1 : 0
  name = aws_ssm_document.start_pss_testbox_document.name
  association_name = "${replace(local.resource_prefix,"_","-")}-Start_pss_testbox"
  schedule_expression = var.pss_testbox_scheduler_start_pattern
  

  parameters = { 
    InstanceId = aws_instance.pss_testbox[0].id
    AutomationAssumeRole = aws_iam_role.pss_testbox_stop_start_role[0].arn
  }
}

resource "aws_ssm_document" "start_pss_testbox_document" {
  count = var.pss_testbox_scheduler_enabled ? 1 : 0
  name          = "Start_PSS_Testbox"
  document_type = "Automation"

  content = <<DOC
{
  "description": "Start EC2 instances(s)",
  "schemaVersion": "0.3",
  "assumeRole": "{{ AutomationAssumeRole }}",
  "parameters": {
    "InstanceId": {
      "type": "StringList",
      "description": "(Required) EC2 Instance(s) to start"
    },
    "AutomationAssumeRole": {
      "type": "String",
      "description": "(Optional) The ARN of the role that allows Automation to perform the actions on your behalf.",
      "default": ""
    }
  },
  "mainSteps": [
    {
      "name": "startInstances",
      "action": "aws:changeInstanceState",
      "inputs": {
        "InstanceIds": "{{ InstanceId }}",
        "DesiredState": "running"
      }
    }
  ]
}
DOC
}*/