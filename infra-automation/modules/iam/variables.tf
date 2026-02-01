variable "policy_name" {
  description = "Name of the IAM policy"
  type        = string
}

variable "policy_description" {
  description = "Description of the IAM policy"
  type        = string
  default     = "IAM policy for agentx"
}

variable "policy_json" {
  description = "The policy document in JSON format"
  type        = string
  default     = null
}

variable "policy_json_path" {
  description = "Path to the policy document JSON file"
  type        = string
  default     = null
}

variable "attach_to_role" {
  description = "Whether to attach the policy to a role"
  type        = bool
  default     = false
}

variable "attach_to_user" {
  description = "Whether to attach the policy to a user"
  type        = bool
  default     = false
}

variable "role_name" {
  description = "Name of the role to attach the policy to"
  type        = string
  default     = null

  validation {
    condition     = !(var.attach_to_role && var.role_name == null)
    error_message = "role_name must be set when attach_to_role is true"
  }
}

variable "user_name" {
  description = "Name of the user to attach the policy to"
  type        = string
  default     = null
}

variable "tags" {
  description = "Tags to assign to the policy"
  type        = map(string)
  default     = {}
} 