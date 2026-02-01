# Network Configuration
vpc_id = "vpc-083b29333479262bc"
subnet_id = "subnet-0e2f65f1c4945e22b"

# Target EC2 instance ID (from EC2 component output)
target_ids = ["i-084cc42cab3b71a7e"]

load_balancers = {
  agentx_alb = {
    name                        = "agentx"
    internal                    = false
    enable_deletion_protection  = false
    target_group_port           = 80
    target_group_protocol       = "HTTP"
    health_check_path           = "/"
    listener_port               = 80
    listener_protocol           = "HTTP"
    tags = {
      Name = "agentx"
      Team = "agentx"
    }
  }
} 