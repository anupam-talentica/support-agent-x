variable "name" {
  description = "Name tag for the instance"
  type        = string
}

variable "ami" {
  description = "AMI ID for the instance"
  type        = string
}

variable "instance_type" {
  description = "EC2 instance type"
  type        = string
}

variable "key_name" {
  description = "Key pair name"
  type        = string
}

variable "subnet_id" {
  description = "Subnet ID to launch the instance in"
  type        = string
}

variable "security_group_ids" {
  description = "List of security group IDs"
  type        = list(string)
}

variable "ebs_type" {
  description = "EBS volume type for root block device"
  type        = string
}

variable "ebs_size" {
  description = "EBS volume size in GB for root block device"
  type        = number
}

variable "disable_api_termination" {
  description = "Enable or disable termination protection"
  type        = bool
}

variable "associate_public_ip_address" {
  description = "Whether to associate a public IP address with the instance"
  type        = bool
}

variable "tags" {
  description = "Map of tags to assign to the instance"
  type        = map(string)
  default     = {}
}

variable "iam_instance_profile" {
  description = "The IAM instance profile to associate with the instance"
  type        = string
  default     = null
} 