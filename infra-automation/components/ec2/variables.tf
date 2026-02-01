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

variable "instances" {
  description = "Map of EC2 instance definitions"
  type = map(object({
    name                        = optional(string)
    ami                         = optional(string)
    instance_type               = optional(string)
    key_name                    = optional(string)
    subnet_id                   = optional(string)
    security_group_ids          = optional(list(string))
    ebs_type                    = optional(string)
    ebs_size                    = optional(number)
    disable_api_termination     = optional(bool)
    associate_public_ip_address = optional(bool)
    tags                        = optional(map(string))
    role_name                   = optional(string)
  }))
  default = {}
}

variable "default_ami" {
  description = "Default AMI ID"
  type        = string
  default     = "ami-0173c04c4bfce9148"
}

variable "default_instance_type" {
  description = "Default EC2 instance type"
  type        = string
  default     = "t4g.medium"
}

variable "default_key_name" {
  description = "Default key pair name"
  type        = string
  default     = "agentx"
}

variable "default_subnet_id" {
  description = "Default subnet ID"
  type        = string
  default     = "subnet-0e2f65f1c4945e22b"
}

variable "default_security_group_ids" {
  description = "Default security group IDs"
  type        = list(string)
  default     = ["sg-0ecfdb9fb90303f17"]
}

variable "default_ebs_type" {
  description = "Default EBS volume type"
  type        = string
  default     = "gp3"
}

variable "default_ebs_size" {
  description = "Default EBS volume size in GB"
  type        = number
  default     = 20
}

variable "default_disable_api_termination" {
  description = "Default termination protection setting"
  type        = bool
  default     = true
}

variable "default_associate_public_ip_address" {
  description = "Default associate public IP address setting"
  type        = bool
  default     = true
} 