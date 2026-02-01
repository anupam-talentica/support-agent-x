locals {
  # Determine the policy path for each bucket
  bucket_policy_paths = {
    for bucket_name, config in var.s3_buckets :
    bucket_name => try(
      config.bucket_policy_path != null ? "${path.module}/${config.bucket_policy_path}" : 
      var.default_bucket_policy_path != null ? "${path.module}/${var.default_bucket_policy_path}" : null,
      null
    )
  }
}

# Create S3 buckets using the module
module "s3_buckets" {
  source   = "../../modules/s3_bucket"
  for_each = var.s3_buckets

  bucket_name          = each.value.bucket_name
  aws_region           = each.value.aws_region
  bucket_type          = each.value.bucket_type
  object_ownership     = each.value.object_ownership
  block_public_access  = each.value.block_public_access
  versioning_enabled   = each.value.versioning_enabled
  default_encryption   = each.value.default_encryption
  bucket_key_enabled   = each.value.bucket_key_enabled
  object_lock_enabled  = each.value.object_lock_enabled
  bucket_policy_path   = local.bucket_policy_paths[each.key]
  enable_static_website = each.value.enable_static_website
  kms_key_id          = each.value.kms_key_id
  tags                = each.value.tags
} 