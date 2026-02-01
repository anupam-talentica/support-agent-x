locals {
  # Process repositories with proper defaults
  repositories = {
    for k, v in var.repositories :
    k => {
      repository_name      = v.repository_name
      image_tag_mutability = coalesce(v.image_tag_mutability, "MUTABLE")
      scan_on_push         = coalesce(v.scan_on_push, true)
      tags = merge({
        Name        = v.repository_name
        Environment = var.environment
        Service     = var.service
        Owner       = var.owner
        Team        = "agentx"
      }, try(v.tags, {}))
    }
  }
}

# Create ECR repositories
module "ecr" {
  source   = "../../modules/ecr"
  for_each = local.repositories

  repository_name      = each.value.repository_name
  image_tag_mutability = each.value.image_tag_mutability
  scan_on_push         = each.value.scan_on_push
  tags                 = each.value.tags
} 