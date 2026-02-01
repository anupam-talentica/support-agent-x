locals {
  # Process load balancers with proper defaults
  load_balancers = {
    for k, v in var.load_balancers :
    k => {
      name                       = v.name
      internal                   = coalesce(v.internal, false)
      enable_deletion_protection = coalesce(v.enable_deletion_protection, false)
      target_group_port          = coalesce(v.target_group_port, 80)
      target_group_protocol      = coalesce(v.target_group_protocol, "HTTP")
      health_check_path          = coalesce(v.health_check_path, "/")
      listener_port              = coalesce(v.listener_port, 80)
      listener_protocol          = coalesce(v.listener_protocol, "HTTP")
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

# Create Application Load Balancers
module "alb" {
  source   = "../../modules/alb"
  for_each = local.load_balancers

  name                       = each.value.name
  internal                   = each.value.internal
  security_group_ids         = var.security_group_ids
  subnet_ids                 = var.subnet_ids
  vpc_id                     = var.vpc_id
  enable_deletion_protection = each.value.enable_deletion_protection
  target_group_port          = each.value.target_group_port
  target_group_protocol      = each.value.target_group_protocol
  health_check_path          = each.value.health_check_path
  listener_port              = each.value.listener_port
  listener_protocol          = each.value.listener_protocol
  target_ids                 = var.target_ids
  tags                       = each.value.tags
} 