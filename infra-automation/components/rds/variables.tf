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
  description = "VPC ID for the RDS instances"
  type        = string
  default     = "vpc-083b29333479262bc"
}

variable "subnet_id" {
  description = "Subnet ID for resources"
  type        = string
  default     = "subnet-0e2f65f1c4945e22b"
}

variable "db_instances" {
  description = "Map of RDS instance configurations"
  type = map(object({
    db_identifier              = string
    engine                     = optional(string, "mysql")
    engine_version             = optional(string, "8.4.7")
    instance_class             = optional(string, "db.t3.micro")
    allocated_storage          = optional(number, 8)
    storage_type               = optional(string, "gp3")
    storage_encrypted          = optional(bool, true)
    kms_key_id                 = optional(string, null)
    db_name                    = optional(string, "agentx")
    master_username            = optional(string, "admin")
    master_password            = string
    vpc_security_group_ids     = list(string)
    create_db_subnet_group     = optional(bool, false)
    db_subnet_group_name       = optional(string, "default")
    subnet_ids                 = optional(list(string), [])
    publicly_accessible        = optional(bool, false)
    skip_final_snapshot        = optional(bool, true)
    backup_retention_period    = optional(number, 7)
    backup_window              = optional(string, "03:00-04:00")
    maintenance_window         = optional(string, "sun:04:00-sun:05:00")
    deletion_protection        = optional(bool, false)
    tags                       = optional(map(string))
  }))
  default = {}
} 