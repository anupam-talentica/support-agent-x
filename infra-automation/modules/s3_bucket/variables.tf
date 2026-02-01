variable "bucket_name" {
  description = "Name of the S3 bucket"
  type        = string
}

variable "aws_region" {
  description = "AWS region for the S3 bucket"
  type        = string
  default     = "ap-south-1"
}

variable "bucket_type" {
  description = "Type of the S3 bucket"
  type        = string
  default     = "General purpose"
}

variable "object_ownership" {
  description = "Object ownership setting for the bucket"
  type        = string
  default     = "Bucket owner enforced"
  validation {
    condition     = contains(["Bucket owner enforced", "ACLs disabled", "ACLs enabled"], var.object_ownership)
    error_message = "Object ownership must be one of: Bucket owner enforced, ACLs disabled, ACLs enabled."
  }
}

variable "block_public_access" {
  description = "Block public access settings for the bucket"
  type = object({
    block_public_acls       = bool
    block_public_policy     = bool
    ignore_public_acls      = bool
    restrict_public_buckets = bool
  })
  default = {
    block_public_acls       = true
    block_public_policy     = true
    ignore_public_acls      = true
    restrict_public_buckets = true
  }
}

variable "versioning_enabled" {
  description = "Enable versioning for the bucket"
  type        = bool
  default     = true
}

variable "default_encryption" {
  description = "Default encryption setting for the bucket"
  type        = string
  default     = "AES256"
  validation {
    condition     = contains(["AES256", "aws:kms"], var.default_encryption)
    error_message = "Default encryption must be either 'AES256' or 'aws:kms'."
  }
}

variable "bucket_key_enabled" {
  description = "Enable bucket key for the bucket"
  type        = bool
  default     = false
}

variable "object_lock_enabled" {
  description = "Enable object lock for the bucket"
  type        = bool
  default     = false
}

variable "bucket_policy_path" {
  description = "Path to the bucket policy JSON file"
  type        = string
  default     = null
  nullable    = true
}

variable "enable_static_website" {
  description = "Enable static website hosting"
  type        = bool
  default     = false
}

variable "tags" {
  description = "Tags to apply to the bucket"
  type = object({
    Name = string
    Team = string
  })
}

variable "kms_key_id" {
  description = "KMS key ID for encryption (required if default_encryption is 'aws:kms')"
  type        = string
  default     = null
} 