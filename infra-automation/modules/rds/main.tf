resource "aws_db_subnet_group" "this" {
  count      = var.create_db_subnet_group ? 1 : 0
  name       = var.db_subnet_group_name
  subnet_ids = var.subnet_ids

  tags = var.tags
}

resource "aws_db_instance" "this" {
  identifier = var.db_identifier

  engine         = var.engine
  engine_version = var.engine_version
  instance_class = var.instance_class

  allocated_storage     = var.allocated_storage
  storage_type          = var.storage_type
  storage_encrypted     = var.storage_encrypted
  kms_key_id           = var.kms_key_id

  db_name  = var.db_name
  username = var.master_username
  password = var.master_password

  vpc_security_group_ids = var.vpc_security_group_ids
  db_subnet_group_name   = var.create_db_subnet_group ? aws_db_subnet_group.this[0].name : var.db_subnet_group_name

  publicly_accessible = var.publicly_accessible
  skip_final_snapshot = var.skip_final_snapshot

  backup_retention_period = var.backup_retention_period
  backup_window          = var.backup_window
  maintenance_window     = var.maintenance_window

  deletion_protection = var.deletion_protection

  tags = var.tags
} 