variable "vpc_id" {
  description = "VPC ID for resources"
  type        = string
  default     = "vpc-083b29333479262bc"
}

variable "subnet_id" {
  description = "Subnet ID for resources"
  type        = string
  default     = "subnet-0e2f65f1c4945e22b"
}

variable "s3_buckets" {
  description = "Map of S3 bucket configurations"
  type = map(object({
    aws_region           = optional(string, "ap-south-1")
    bucket_type          = optional(string, "General purpose")
    bucket_name          = string
    object_ownership     = optional(string, "Bucket owner enforced")
    block_public_access = optional(object({
      block_public_acls       = bool
      block_public_policy     = bool
      ignore_public_acls      = bool
      restrict_public_buckets = bool
    }), {
      block_public_acls       = true
      block_public_policy     = true
      ignore_public_acls      = true
      restrict_public_buckets = true
    })
    versioning_enabled   = optional(bool, true)
    default_encryption   = optional(string, "AES256")
    bucket_key_enabled   = optional(bool, false)
    object_lock_enabled  = optional(bool, false)
    bucket_policy_path   = optional(string, null)
    enable_static_website = optional(bool, false)
    kms_key_id          = optional(string, null)
    tags = object({
      Name = string
      Team = string
    })
  }))
}

variable "default_bucket_policy_path" {
  description = "Path to the default bucket policy file"
  type        = string
  default     = "policies/default-bucket-policy.json"
} 