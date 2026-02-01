output "instance_summary" {
  description = "Map of instance name to public IP, private IP, and IAM role attached"
  value = {
    for k, v in local.instances :
    k => {
      public_ip  = try(module.ec2[k].public_ip, null)
      private_ip = try(module.ec2[k].private_ip, null)
      iam_role   = v.role_name
      instance_profile = null
      arn        = try(module.ec2[k].arn, null)
    }
  }
}

output "instance_ids" {
  description = "Map of instance name to instance ID"
  value = { for k, m in module.ec2 : k => m.instance_id }
}

output "public_ips" {
  description = "Map of instance name to public IP address"
  value = { for k, m in module.ec2 : k => m.public_ip }
}

output "private_ips" {
  description = "Map of instance name to private IP address"
  value = { for k, m in module.ec2 : k => m.private_ip }
}

output "instance_arns" {
  description = "Map of instance name to instance ARN"
  value = { for k, m in module.ec2 : k => m.arn }
} 