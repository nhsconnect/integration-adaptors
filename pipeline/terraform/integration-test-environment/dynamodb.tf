resource "aws_dynamodb_table" "mhs_state_table" {
    name           = "${var.build_id}-mhs-state"
    hash_key       = "key"
    read_capacity  = var.mhs_state_table_read_capacity
    write_capacity = var.mhs_state_table_write_capacity

    attribute {
        name = "key"
        type = "S"
    }

  tags = {
    Name = "${var.build_id}-mhs-state-table"
    BuildId = var.build_id
  }
}

resource "aws_dynamodb_table" "mhs_sync_async_table" {
    name           = "${var.build_id}-mhs-sync-async-state"
    hash_key       = "key"
    read_capacity  = var.mhs_sync_async_table_read_capacity
    write_capacity = var.mhs_sync_async_table_write_capacity

    attribute {
        name = "key"
        type = "S"
    }

  tags = {
    Name = "${var.build_id}-mhs-sync-async-table"
    BuildId = var.build_id
  }
}
