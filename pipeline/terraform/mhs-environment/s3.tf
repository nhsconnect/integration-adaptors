####################
# S3 bucket for MHS load balancer logs
####################

# Get the elastic load balancing account ID for the current AWS region.
# This account is the one that AWS elastic load balancing uses to publish
# access logs into S3.
# See https://docs.aws.amazon.com/elasticloadbalancing/latest/application/load-balancer-access-logs.html#access-logging-bucket-permissions
# for more info.
data "aws_elb_service_account" "main" {}

# S3 bucket for storing MHS load balancer access logs
resource "aws_s3_bucket" "mhs_access_logs_bucket" {
  bucket = "${var.environment_id}-mhs-access-logs-bucket"
  server_side_encryption_configuration {

    rule {
      apply_server_side_encryption_by_default {
        sse_algorithm = "AES256"
      }
    }
  }

  tags = {
    Name = "${var.environment_id}-mhs-access-logs-bucket"
    EnvironmentId = var.environment_id
  }
}

# S3 bucket policy for MHS access logs bucket.
# This policy is based on the AWS documentation
# https://docs.aws.amazon.com/elasticloadbalancing/latest/application/load-balancer-access-logs.html#access-logging-bucket-permissions
# and https://docs.aws.amazon.com/elasticloadbalancing/latest/network/load-balancer-access-logs.html
resource "aws_s3_bucket_policy" "mhs_access_logs_bucket_policy" {
  bucket = aws_s3_bucket.mhs_access_logs_bucket.id

  policy = jsonencode(
  {
    Id = "MHSAccessLogsBucketPolicy"
    Version = "2012-10-17"
    Statement = [
      {
        Sid = "AllowELBAccess"
        Action = "s3:PutObject"
        Effect = "Allow"
        Resource = "arn:aws:s3:::${aws_s3_bucket.mhs_access_logs_bucket.bucket}/*"
        Principal = {
          AWS = data.aws_elb_service_account.main.arn
        }
      },
      {
      Sid = "AWSLogDeliveryWrite"
      Action= "s3:PutObject"
      Effect = "Allow"
      Principal= {
        Service= "delivery.logs.amazonaws.com"
      }
      Resource= "arn:aws:s3:::${aws_s3_bucket.mhs_access_logs_bucket.bucket}/*"
      Condition= {
        StringEquals= {
          "s3:x-amz-acl" = "bucket-owner-full-control"
        }
      }
    },
    {
      Sid= "AWSLogDeliveryAclCheck"
      Action= "s3:GetBucketAcl"
      Effect= "Allow"
      Principal= {
        Service= "delivery.logs.amazonaws.com"
      }
      Resource= "arn:aws:s3:::${aws_s3_bucket.mhs_access_logs_bucket.bucket}"
    }
    ]
  }
  )
}

# Disable any public access to MHS access logs bucket
resource "aws_s3_bucket_public_access_block" "mhs_access_logs_bucket_public_access_block" {
  bucket = aws_s3_bucket.mhs_access_logs_bucket.id

  block_public_acls = true
  block_public_policy = true
  ignore_public_acls = true
  restrict_public_buckets = true

  # Need to make sure not to try and disable public access at the same time as adding the
  # bucket policy, as trying to do both at the same time results in an error.
  depends_on = [
    aws_s3_bucket_policy.mhs_access_logs_bucket_policy
  ]
}
