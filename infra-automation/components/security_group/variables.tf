variable "environment" {
  description = "Deployment environment"
  type        = string
  default     = "hackathon"
}

variable "service" {
  description = "Service name"
  type        = string
  default     = "agentx"
}

variable "owner" {
  description = "Owner of the resource"
  type        = string
  default     = "agentx"
}

variable "vpc_id" {
  description = "VPC ID for security groups"
  type        = string
  default     = "vpc-083b29333479262bc"
}

variable "subnet_id" {
  description = "Subnet ID for resources"
  type        = string
  default     = "subnet-0e2f65f1c4945e22b"
}

variable "security_groups" {
  description = "Map of security group configurations"
  type = map(object({
    name        = string
    description = string
    vpc_id      = optional(string)
    inbound_rules = list(object({
      description = optional(string)
      from_port   = number
      to_port     = number
      protocol    = string
      cidr_blocks = optional(list(string))
      security_groups = optional(list(string))
      self        = optional(bool)
    }))
    outbound_rules = optional(list(object({
      description = optional(string)
      from_port   = number
      to_port     = number
      protocol    = string
      cidr_blocks = optional(list(string))
      security_groups = optional(list(string))
      self        = optional(bool)
    })))
    tags = optional(map(string))
  }))
  default = {}
} 