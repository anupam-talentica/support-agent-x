output "repository_summary" {
  description = "Map of repository names to their details"
  value = {
    for k, m in module.ecr : k => {
      url = m.repository_url
      arn = m.repository_arn
    }
  }
}

output "repository_urls" {
  description = "Map of repository names to their URLs"
  value = { for k, m in module.ecr : k => m.repository_url }
}

output "repository_arns" {
  description = "Map of repository names to their ARNs"
  value = { for k, m in module.ecr : k => m.repository_arn }
} 