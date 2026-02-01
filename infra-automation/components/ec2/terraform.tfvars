# Network Configuration
vpc_id = "vpc-083b29333479262bc"
subnet_id = "subnet-0e2f65f1c4945e22b"

instances = {
  "agentx" = {
    name                        = "agentx"
    ami                         = "ami-0848881f2a3dcebd1"
    instance_type               = "t4g.large"
    key_name                    = "agentx"
    subnet_id                   = "subnet-0e2f65f1c4945e22b"
    security_group_ids          = ["sg-0ecfdb9fb90303f17"]
    ebs_type                    = "gp3"
    ebs_size                    = 20
    disable_api_termination     = true
    associate_public_ip_address = true
    role_name                   = "agentx"
    tags = {
      Name = "agentx"
      Team = "agentx"
    }
  }
} 