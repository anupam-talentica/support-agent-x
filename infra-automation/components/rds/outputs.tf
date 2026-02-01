output "db_instance_summary" {
  description = "Map of database instance names to their details"
  value = {
    for k, m in module.rds : k => {
      id       = m.db_instance_id
      arn      = m.db_instance_arn
      endpoint = m.db_instance_endpoint
      address  = m.db_instance_address
      port     = m.db_instance_port
      username = m.db_instance_username
      name     = m.db_instance_name
    }
  }
}

output "db_endpoints" {
  description = "Map of database instance names to their endpoints"
  value = { for k, m in module.rds : k => m.db_instance_endpoint }
}

output "db_addresses" {
  description = "Map of database instance names to their addresses"
  value = { for k, m in module.rds : k => m.db_instance_address }
}

output "db_ports" {
  description = "Map of database instance names to their ports"
  value = { for k, m in module.rds : k => m.db_instance_port }
} 