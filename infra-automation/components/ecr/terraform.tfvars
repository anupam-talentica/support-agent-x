# Network Configuration
vpc_id = "vpc-083b29333479262bc"
subnet_id = "subnet-0e2f65f1c4945e22b"

repositories = {
  agentx_repo = {
    repository_name      = "agentx"
    image_tag_mutability = "MUTABLE"
    scan_on_push         = true
    tags = {
      Name = "agentx"
      Team = "agentx"
    }
  }
} 