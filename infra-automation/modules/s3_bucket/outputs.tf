output "bucket_name" {
  description = "Name of the S3 bucket"
  value       = aws_s3_bucket.this.bucket
}

output "bucket_arn" {
  description = "ARN of the S3 bucket"
  value       = aws_s3_bucket.this.arn
}

output "bucket_id" {
  description = "ID of the S3 bucket"
  value       = aws_s3_bucket.this.id
}

output "bucket_region" {
  description = "Region of the S3 bucket"
  value       = aws_s3_bucket.this.region
}

output "bucket_policy_attached" {
  description = "Whether a bucket policy is attached"
  value       = var.bucket_policy_path != null
}

output "bucket_policy_path" {
  description = "Path to the bucket policy file"
  value       = var.bucket_policy_path
}

output "versioning_enabled" {
  description = "Whether versioning is enabled"
  value       = var.versioning_enabled
}

output "encryption_type" {
  description = "Type of encryption used"
  value       = var.default_encryption
}

output "object_lock_enabled" {
  description = "Whether object lock is enabled"
  value       = var.object_lock_enabled
}

output "website_endpoint" {
  description = "The website endpoint URL"
  value       = var.enable_static_website ? aws_s3_bucket_website_configuration.this[0].website_endpoint : null
}

output "website_domain" {
  description = "The website domain"
  value       = var.enable_static_website ? aws_s3_bucket_website_configuration.this[0].website_domain : null
} 