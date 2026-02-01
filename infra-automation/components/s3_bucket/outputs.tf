output "bucket_names" {
  description = "Names of all created S3 buckets"
  value = {
    for bucket_name, bucket in module.s3_buckets :
    bucket_name => bucket.bucket_name
  }
}

output "bucket_arns" {
  description = "ARNs of all created S3 buckets"
  value = {
    for bucket_name, bucket in module.s3_buckets :
    bucket_name => bucket.bucket_arn
  }
}

output "bucket_policies" {
  description = "Bucket policy information for each bucket"
  value = {
    for bucket_name, bucket in module.s3_buckets :
    bucket_name => {
      policy_attached = bucket.bucket_policy_attached
      policy_path     = bucket.bucket_policy_path
    }
  }
}

output "bucket_configurations" {
  description = "Complete configuration details for each bucket"
  value = {
    for bucket_name, bucket in module.s3_buckets :
    bucket_name => {
      name                = bucket.bucket_name
      arn                 = bucket.bucket_arn
      region              = bucket.bucket_region
      versioning_enabled  = bucket.versioning_enabled
      encryption_type     = bucket.encryption_type
      object_lock_enabled = bucket.object_lock_enabled
      policy_attached     = bucket.bucket_policy_attached
      policy_path         = bucket.bucket_policy_path
      website_endpoint    = bucket.website_endpoint
      website_domain      = bucket.website_domain
    }
  }
}

output "total_buckets" {
  description = "Total number of S3 buckets created"
  value       = length(module.s3_buckets)
} 