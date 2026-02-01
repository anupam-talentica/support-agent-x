# Network Configuration
vpc_id = "vpc-083b29333479262bc"
subnet_id = "subnet-0e2f65f1c4945e22b"

security_groups = {
  agentx_sg = {
    name        = "agentx-sg"
    description = "Security group for agentx"
    inbound_rules = [
      {
        description = "SSH access"
        from_port   = 22
        to_port     = 22
        protocol    = "tcp"
        cidr_blocks = ["0.0.0.0/0"]
      },
      {
        description = "HTTP access"
        from_port   = 80
        to_port     = 80
        protocol    = "tcp"
        cidr_blocks = ["0.0.0.0/0"]
      },
      {
        description = "HTTPS access"
        from_port   = 443
        to_port     = 443
        protocol    = "tcp"
        cidr_blocks = ["0.0.0.0/0"]
      },
      {
        description = "MySQL access"
        from_port   = 3306
        to_port     = 3306
        protocol    = "tcp"
        cidr_blocks = ["0.0.0.0/0"]
      }
    ]
    outbound_rules = [
      {
        description = "All traffic"
        from_port   = 0
        to_port     = 0
        protocol    = "-1"
        cidr_blocks = ["0.0.0.0/0"]
      }
    ]
    tags = {
      Name = "agentx"
      Team = "agentx"
    }
  }
} 