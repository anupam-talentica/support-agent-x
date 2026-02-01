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
  description = "VPC ID for resources"
  type        = string
  default     = "vpc-083b29333479262bc"
}

variable "subnet_id" {
  description = "Subnet ID for resources"
  type        = string
  default     = "subnet-0e2f65f1c4945e22b"
}

variable "repositories" {
  description = "Map of ECR repositories to create"
  type = map(object({
    repository_name      = string
    image_tag_mutability = optional(string, "MUTABLE")
    scan_on_push         = optional(bool, true)
    tags                 = optional(map(string))
  }))
  default = {}
} 