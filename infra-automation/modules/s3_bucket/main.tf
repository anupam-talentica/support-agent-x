# S3 Bucket
resource "aws_s3_bucket" "this" {
  bucket = var.bucket_name
  tags   = var.tags
}

# Object Ownership
resource "aws_s3_bucket_ownership_controls" "this" {
  bucket = aws_s3_bucket.this.id

  rule {
    object_ownership = var.object_ownership == "Bucket owner enforced" ? "BucketOwnerEnforced" : (var.object_ownership == "ACLs disabled" ? "BucketOwnerPreferred" : "ObjectWriter")
  }
}

# Block Public Access
resource "aws_s3_bucket_public_access_block" "this" {
  bucket = aws_s3_bucket.this.id

  block_public_acls       = var.block_public_access.block_public_acls
  block_public_policy     = var.block_public_access.block_public_policy
  ignore_public_acls      = var.block_public_access.ignore_public_acls
  restrict_public_buckets = var.block_public_access.restrict_public_buckets
}

# Versioning
resource "aws_s3_bucket_versioning" "this" {
  bucket = aws_s3_bucket.this.id

  versioning_configuration {
    status = var.versioning_enabled ? "Enabled" : "Disabled"
  }
}

# Default Encryption
resource "aws_s3_bucket_server_side_encryption_configuration" "this" {
  bucket = aws_s3_bucket.this.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm     = var.default_encryption == "AES256" ? "AES256" : "aws:kms"
      kms_master_key_id = var.default_encryption == "aws:kms" ? var.kms_key_id : null
    }
    bucket_key_enabled = var.bucket_key_enabled
  }
}

# Object Lock (only if enabled)
resource "aws_s3_bucket_object_lock_configuration" "this" {
  count  = var.object_lock_enabled ? 1 : 0
  bucket = aws_s3_bucket.this.id

  rule {
    default_retention {
      mode = "GOVERNANCE"
      days = 1
    }
  }
}

# Bucket Policy (if provided)
resource "aws_s3_bucket_policy" "this" {
  count  = var.bucket_policy_path != null ? 1 : 0
  bucket = aws_s3_bucket.this.id

  policy = file(var.bucket_policy_path)
}

# Website Configuration for Static Hosting
resource "aws_s3_bucket_website_configuration" "this" {
  count  = var.enable_static_website ? 1 : 0
  bucket = aws_s3_bucket.this.id

  index_document {
    suffix = "index.html"
  }

  error_document {
    key = "error.html"
  }
} 