# Network Configuration
vpc_id = "vpc-083b29333479262bc"
subnet_id = "subnet-0e2f65f1c4945e22b"

s3_buckets = {
  agentx_bucket = {
    aws_region       = "ap-south-1"
    bucket_type      = "General purpose"
    bucket_name      = "agentx-hck2026"
    object_ownership = "Bucket owner enforced"
    
    block_public_access = {
      block_public_acls       = false
      block_public_policy     = false
      ignore_public_acls      = false
      restrict_public_buckets = false
    }
    
    versioning_enabled  = true
    default_encryption  = "AES256"
    bucket_key_enabled  = false
    object_lock_enabled = false
    bucket_policy_path  = "policies/agentx.json"
    enable_static_website = true
    
    tags = {
      Name = "agentx"
      Team = "agentx"
    }
  }
} 