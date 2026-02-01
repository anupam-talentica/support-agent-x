output "policy_summary" {
  description = "Map of policy names to their details"
  value = {
    for k, m in module.iam : k => {
      arn  = m.policy_arn
      id   = m.policy_id
      name = m.policy_name
    }
  }
}

output "policy_arns" {
  description = "Map of policy names to their ARNs"
  value = { for k, m in module.iam : k => m.policy_arn }
}

output "policy_names" {
  description = "Map of policy names to their names"
  value = { for k, m in module.iam : k => m.policy_name }
} 