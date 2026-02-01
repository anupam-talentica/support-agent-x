output "security_group_ids" {
  description = "Map of security group names to their IDs"
  value       = { for k, m in module.security_group : k => m.security_group_id }
}

output "security_group_names" {
  description = "Map of security group names to their names"
  value       = { for k, m in module.security_group : k => m.security_group_name }
}

output "security_group_arns" {
  description = "Map of security group names to their ARNs"
  value       = { for k, m in module.security_group : k => m.security_group_arn }
} 