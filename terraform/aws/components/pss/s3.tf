resource "aws_s3_bucket" "pss_attachment_bucket" {
  bucket = "${local.resource_prefix}-attachment-storage-bucket"
  tags = merge(local.default_tags, {
      Name = "${local.resource_prefix}-attachment-storage-bucket"
    })
}

resource "aws_s3_bucket_lifecycle_configuration" "pss_attachment_bucket_lifecycle_config" {
  bucket = aws_s3_bucket.pss_attachment_bucket.id
  rule {
    id     = "attachment_retention_period"
    status = "Enabled"
    expiration {
      days = var.pss_attachment_bucket_retention_period
    }
  }
}

resource "aws_s3_bucket_policy" "pss_attachment_bucket_policy" {
  bucket = aws_s3_bucket.pss_attachment_bucket.id

  policy = jsonencode(
    {
      Id = "PssAttachmentStorageBucketPolicy"
      Version = "2012-10-17"
      Statement = [
        {
          Sid = "AllowECSTaskRole"
          Effect = "Allow"
          Action = [
            "s3:PutObject",
            "s3:GetObject",
            "s3:DeleteObject"
          ]
          Resource = "${aws_s3_bucket.pss_attachment_bucket.arn}/*"
          Principal = {
            AWS = data.aws_iam_role.ecs_service_task_role.arn
          }
        }
      ]
    }
  )
}

resource "aws_s3_bucket_public_access_block" "pss_attachment_bucket_public_access_block" {
  bucket = aws_s3_bucket.pss_attachment_bucket.id

  block_public_acls = true
  block_public_policy = true
  ignore_public_acls = true
  restrict_public_buckets = true

  depends_on = [
    aws_s3_bucket_policy.pss_attachment_bucket_policy
  ]
}