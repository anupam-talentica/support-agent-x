resource "aws_instance" "this" {
  ami                         = var.ami
  instance_type               = var.instance_type
  key_name                    = var.key_name
  subnet_id                   = var.subnet_id
  vpc_security_group_ids      = var.security_group_ids
  associate_public_ip_address = var.associate_public_ip_address
  disable_api_termination     = var.disable_api_termination

  root_block_device {
    volume_type = var.ebs_type
    volume_size = var.ebs_size
  }

  tags = merge({
    Name = var.name
  }, var.tags)
} 