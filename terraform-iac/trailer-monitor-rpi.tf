terraform {
  required_version = "1.0.2"
  backend "s3" {
    bucket         = "terraform-state-storage-300328088357"
    dynamodb_table = "terraform-state-lock-300328088357"
    key            = "trailer-monitor-rpi.tfstate"
    region         = "us-west-2"
  }
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "3.49.0"
    }
  }
}

provider "aws" {
  region = "us-west-2"
}

locals {
  name = "trailer-monitor-rpi"
}

resource "aws_s3_bucket" "my_s3_bucket" {
  bucket = local.name
  lifecycle_rule {
    id                                     = "AutoAbortFailedMultipartUpload"
    enabled                                = true
    abort_incomplete_multipart_upload_days = 10
  }
  server_side_encryption_configuration {
    rule {
      apply_server_side_encryption_by_default {
        sse_algorithm = "AES256"
      }
    }
  }
}

resource "aws_s3_bucket_public_access_block" "default" {
  bucket                  = aws_s3_bucket.my_s3_bucket.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_iam_user" "my_user" {
  name = local.name
}

resource "aws_iam_access_key" "my_key" {
  user    = aws_iam_user.my_user.name
  pgp_key = "keybase:joshgubler"
}

resource "aws_iam_user_policy" "my_s3_policy" {
  name = "${local.name}-s3"
  user = aws_iam_user.my_user.name

  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:ListBucket"
      ],
      "Resource": [
        "${aws_s3_bucket.my_s3_bucket.arn}"
      ]
    },
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject"
      ],
      "Resource": [
        "${aws_s3_bucket.my_s3_bucket.arn}/*"
      ]
    }
  ]
}
EOF
}

output "aws_access_key_id" {
  value = aws_iam_access_key.my_key.id
}

output "aws_secret_access_key" {
  value = aws_iam_access_key.my_key.encrypted_secret
}

