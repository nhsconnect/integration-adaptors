#########################
# DynamoDB tables
#
# Note that AWS by default encrypts DynamoDB tables at rest using an
# AWS-owned customer master key. This can be changed later to an
# AWS-managed customer master key.
# See https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/EncryptionAtRest.html
# for more details.
#########################

# The MHS DynamoDB state table, for storing state for each message handled
resource "aws_dynamodb_table" "mhs_state_table" {
  name = "${var.environment_id}-mhs-state"
  hash_key = "key"
  read_capacity = var.mhs_state_table_read_capacity
  write_capacity = var.mhs_state_table_write_capacity

  attribute {
    name = "key"
    type = "S"
  }

  tags = {
    Name = "${var.environment_id}-mhs-state-table"
    EnvironmentId = var.environment_id
  }
}

# The MHS DynamoDB sync-async table, used as a queue for the sync-async workflow
resource "aws_dynamodb_table" "mhs_sync_async_table" {
  name = "${var.environment_id}-mhs-sync-async-state"
  hash_key = "key"
  read_capacity = var.mhs_sync_async_table_read_capacity
  write_capacity = var.mhs_sync_async_table_write_capacity

  attribute {
    name = "key"
    type = "S"
  }

  tags = {
    Name = "${var.environment_id}-mhs-sync-async-table"
    EnvironmentId = var.environment_id
  }
}

# Terraform output variable of the DynamoDB table used to store the MHS state
output "mhs_state_table_name" {
  value = aws_dynamodb_table.mhs_state_table.name
  description = "The name of the DynamoDB table used to store the MHS state"
}

# Terraform output variable of the DynamoDB table used to store the MHS inbound/outbound communication state
output "mhs_sync_async_table_name" {
  value = aws_dynamodb_table.mhs_sync_async_table.name
  description = "The name of the DynamoDB table used to store the MHS inbound/outbound communication state"
}
