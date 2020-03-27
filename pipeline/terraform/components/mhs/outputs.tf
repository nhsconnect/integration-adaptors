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