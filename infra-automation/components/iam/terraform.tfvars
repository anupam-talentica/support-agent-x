# Network Configuration
vpc_id = "vpc-083b29333479262bc"
subnet_id = "subnet-0e2f65f1c4945e22b"

policies = {
  agentx_policy = {
    policy_name        = "agentx-Policy"
    policy_description = "Comprehensive IAM policy for agentx hackathon project"
    policy_json_path   = "policies/agentx-policy.json"
    attach_to_role     = true
    role_name          = "agentx"
    tags = {
      Name = "agentx"
      Team = "agentx"
    }
  }
} 