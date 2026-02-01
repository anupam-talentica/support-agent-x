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
  description = "VPC ID for the load balancer"
  type        = string
  default     = "vpc-083b29333479262bc"
}

variable "subnet_id" {
  description = "Subnet ID for resources"
  type        = string
  default     = "subnet-0e2f65f1c4945e22b"
}

variable "subnet_ids" {
  description = "List of subnet IDs for the load balancer"
  type        = list(string)
  default     = ["subnet-0e2f65f1c4945e22b", "subnet-08f09cad3ac7d6a07", "subnet-0bf20093c3bf8785b"]
}

variable "security_group_ids" {
  description = "List of security group IDs for the load balancer"
  type        = list(string)
  default     = ["sg-0ecfdb9fb90303f17"]
}

variable "target_ids" {
  description = "List of target IDs to attach to the target group"
  type        = list(string)
  default     = []
}

variable "load_balancers" {
  description = "Map of load balancer configurations"
  type = map(object({
    name                        = string
    internal                    = optional(bool, false)
    enable_deletion_protection  = optional(bool, false)
    target_group_port           = optional(number, 80)
    target_group_protocol       = optional(string, "HTTP")
    health_check_path           = optional(string, "/")
    listener_port               = optional(number, 80)
    listener_protocol           = optional(string, "HTTP")
    tags                        = optional(map(string))
  }))
  default = {}
} 