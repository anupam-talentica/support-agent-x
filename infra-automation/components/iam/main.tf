locals {
  # Process policies with proper defaults
  policies = {
    for k, v in var.policies :
    k => {
      policy_name        = v.policy_name
      policy_description = coalesce(v.policy_description, "IAM policy for agentx")
      policy_json        = try(v.policy_json, null)
      policy_json_path   = try(v.policy_json_path, null)
      attach_to_role     = coalesce(v.attach_to_role, false)
      attach_to_user     = coalesce(v.attach_to_user, false)
      role_name          = v.role_name
      user_name          = v.user_name
      tags = merge({
        Name        = v.policy_name
        Environment = var.environment
        Service     = var.service
        Owner       = var.owner
        Team        = "agentx"
      }, try(v.tags, {}))
    }
  }
}

# Create IAM policies
module "iam" {
  source   = "../../modules/iam"
  for_each = local.policies

  policy_name        = each.value.policy_name
  policy_description = each.value.policy_description
  policy_json        = each.value.policy_json
  policy_json_path   = each.value.policy_json_path
  attach_to_role     = each.value.attach_to_role
  attach_to_user     = each.value.attach_to_user
  role_name          = each.value.role_name
  user_name          = each.value.user_name
  tags               = each.value.tags
} 