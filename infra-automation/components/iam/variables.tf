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

variable "policies" {
  description = "Map of IAM policy configurations"
  type = map(object({
    policy_name        = string
    policy_description = optional(string, "IAM policy for agentx")
    policy_json        = optional(string, null)
    policy_json_path   = optional(string, null)
    attach_to_role     = optional(bool, false)
    attach_to_user     = optional(bool, false)
    role_name          = optional(string, null)
    user_name          = optional(string, null)
    tags               = optional(map(string))
  }))
  default = {}
} 