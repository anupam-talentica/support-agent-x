output "security_group_id" {
  description = "The ID of the security group"
  value       = aws_security_group.this.id
}

output "security_group_arn" {
  description = "The ARN of the security group"
  value       = aws_security_group.this.arn
}

output "security_group_name" {
  description = "The name of the security group"
  value       = aws_security_group.this.name
}

output "security_group_description" {
  description = "The description of the security group"
  value       = aws_security_group.this.description
}

output "vpc_id" {
  description = "The VPC ID where the security group is created"
  value       = aws_security_group.this.vpc_id
} 