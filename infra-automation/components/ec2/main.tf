locals {
  # Process instances with proper defaults
  instances = {
    for k, v in var.instances :
    k => {
      name                        = coalesce(v.name, k)
      ami                         = coalesce(v.ami, var.default_ami)
      instance_type               = coalesce(v.instance_type, var.default_instance_type)
      key_name                    = coalesce(v.key_name, var.default_key_name)
      subnet_id                   = coalesce(v.subnet_id, var.default_subnet_id)
      security_group_ids          = coalesce(v.security_group_ids, var.default_security_group_ids)
      ebs_type                    = coalesce(v.ebs_type, var.default_ebs_type)
      ebs_size                    = coalesce(v.ebs_size, var.default_ebs_size)
      disable_api_termination     = coalesce(v.disable_api_termination, var.default_disable_api_termination)
      associate_public_ip_address = coalesce(v.associate_public_ip_address, var.default_associate_public_ip_address)
      tags = merge({
        Environment = var.environment
        Service     = var.service
        Owner       = var.owner
        Team        = "agentx"
      }, try(v.tags, {}))
      role_name = try(v.role_name, null)
    }
  }
}

# Create EC2 instances using the module
module "ec2" {
  source = "../../modules/ec2"
  for_each = local.instances

  name                        = each.value.name
  ami                         = each.value.ami
  instance_type               = each.value.instance_type
  key_name                    = each.value.key_name
  subnet_id                   = each.value.subnet_id
  security_group_ids          = each.value.security_group_ids
  ebs_type                    = each.value.ebs_type
  ebs_size                    = each.value.ebs_size
  disable_api_termination     = each.value.disable_api_termination
  associate_public_ip_address = each.value.associate_public_ip_address
  tags                        = each.value.tags
} 