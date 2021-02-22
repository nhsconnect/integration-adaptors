
# S3 bucket for storing extracts as cache
resource "aws_s3_bucket" "gp2gp_extract_cache_bucket" {
  bucket = "${var.environment_id}-gp2gp-extract-cache-bucket"
  tags = {
    Name = "${var.environment_id}-gp2gp-extract-cache-bucket"
    EnvironmentId = var.environment_id
  }
  lifecycle_rule {
    id      = "cache_retention_period"
    enabled = true
    expiration {
      days = var.gp2gp_extract_cache_bucket_retention_period
    }
  }
}

# S3 bucket policy for GP2GP extract cache bucket.

resource "aws_s3_bucket_policy" "gp2gp_extract_cache_bucket_policy" {
  bucket = aws_s3_bucket.gp2gp_extract_cache_bucket.id

  policy = jsonencode(
  {
    Id = "GP2GPExtractCacheBucketPolicy"
    Version = "2012-10-17"
    Statement = [
      {
        Sid = "AllowECSTaskRole"
        Effect = "Allow"
        Action = [
          "s3:PutObject",
          "s3:GetObject"
        ]
        Resource = "${aws_s3_bucket.gp2gp_extract_cache_bucket.arn}/*" 
        Principal = {
          AWS = data.aws_iam_role.ecs_service_task_role.arn
        }
      }
    ]
  }
  )
}

# Disable any public access to bucket
resource "aws_s3_bucket_public_access_block" "gp2gp_extract_cache_bucket_public_access_block" {
  bucket = aws_s3_bucket.gp2gp_extract_cache_bucket.id

  block_public_acls = true
  block_public_policy = true
  ignore_public_acls = true
  restrict_public_buckets = true

  # Need to make sure not to try and disable public access at the same time as adding the
  # bucket policy, as trying to do both at the same time results in an error.
  depends_on = [
    aws_s3_bucket_policy.gp2gp_extract_cache_bucket_policy
  ]
}
