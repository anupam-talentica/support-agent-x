locals {
  # Process security groups with proper defaults
  security_groups = {
    for k, v in var.security_groups :
    k => {
      name        = v.name
      description = v.description
      vpc_id      = coalesce(v.vpc_id, var.vpc_id)
      inbound_rules  = v.inbound_rules
      outbound_rules = try(v.outbound_rules, [
        {
          description = "All traffic"
          from_port   = 0
          to_port     = 0
          protocol    = "-1"
          cidr_blocks = ["0.0.0.0/0"]
        }
      ])
      tags = merge({
        Name        = v.name
        Environment = var.environment
        Service     = var.service
        Owner       = var.owner
        Team        = "agentx"
      }, try(v.tags, {}))
    }
  }
}

module "security_group" {
  source   = "../../modules/security_group"
  for_each = local.security_groups

  name           = each.value.name
  description    = each.value.description
  vpc_id         = each.value.vpc_id
  inbound_rules  = each.value.inbound_rules
  outbound_rules = each.value.outbound_rules
  tags           = each.value.tags
} 