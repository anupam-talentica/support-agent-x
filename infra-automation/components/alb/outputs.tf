output "load_balancer_summary" {
  description = "Map of load balancer names to their details"
  value = {
    for k, m in module.alb : k => {
      id          = m.load_balancer_id
      arn         = m.load_balancer_arn
      dns_name    = m.load_balancer_dns_name
      zone_id     = m.load_balancer_zone_id
      target_group_arn = m.target_group_arn
      target_group_name = m.target_group_name
      listener_arn = m.listener_arn
    }
  }
}

output "load_balancer_dns_names" {
  description = "Map of load balancer names to their DNS names"
  value = { for k, m in module.alb : k => m.load_balancer_dns_name }
}

output "load_balancer_zone_ids" {
  description = "Map of load balancer names to their zone IDs"
  value = { for k, m in module.alb : k => m.load_balancer_zone_id }
} 