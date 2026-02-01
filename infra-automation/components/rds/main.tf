locals {
  # Process RDS instances with proper defaults
  db_instances = {
    for k, v in var.db_instances :
    k => {
      db_identifier              = v.db_identifier
      engine                     = coalesce(v.engine, "mysql")
      engine_version             = coalesce(v.engine_version, "8.0.35")
      instance_class             = coalesce(v.instance_class, "db.t3.micro")
      allocated_storage          = coalesce(v.allocated_storage, 8)
      storage_type               = coalesce(v.storage_type, "gp2")
      storage_encrypted          = coalesce(v.storage_encrypted, true)
      kms_key_id                 = v.kms_key_id
      db_name                    = coalesce(v.db_name, "agentx")
      master_username            = coalesce(v.master_username, "admin")
      master_password            = v.master_password
      vpc_security_group_ids     = v.vpc_security_group_ids
      create_db_subnet_group     = coalesce(v.create_db_subnet_group, false)
      db_subnet_group_name       = coalesce(v.db_subnet_group_name, "default")
      subnet_ids                 = coalesce(v.subnet_ids, [])
      publicly_accessible        = coalesce(v.publicly_accessible, false)
      skip_final_snapshot        = coalesce(v.skip_final_snapshot, true)
      backup_retention_period    = coalesce(v.backup_retention_period, 7)
      backup_window              = coalesce(v.backup_window, "03:00-04:00")
      maintenance_window         = coalesce(v.maintenance_window, "sun:04:00-sun:05:00")
      deletion_protection        = coalesce(v.deletion_protection, false)
      tags = merge({
        Name        = v.db_identifier
        Environment = var.environment
        Service     = var.service
        Owner       = var.owner
        Team        = "agentx"
      }, try(v.tags, {}))
    }
  }
}

# Create RDS instances
module "rds" {
  source   = "../../modules/rds"
  for_each = local.db_instances

  db_identifier              = each.value.db_identifier
  engine                     = each.value.engine
  engine_version             = each.value.engine_version
  instance_class             = each.value.instance_class
  allocated_storage          = each.value.allocated_storage
  storage_type               = each.value.storage_type
  storage_encrypted          = each.value.storage_encrypted
  kms_key_id                 = each.value.kms_key_id
  db_name                    = each.value.db_name
  master_username            = each.value.master_username
  master_password            = each.value.master_password
  vpc_security_group_ids     = each.value.vpc_security_group_ids
  create_db_subnet_group     = each.value.create_db_subnet_group
  db_subnet_group_name       = each.value.db_subnet_group_name
  subnet_ids                 = each.value.subnet_ids
  publicly_accessible        = each.value.publicly_accessible
  skip_final_snapshot        = each.value.skip_final_snapshot
  backup_retention_period    = each.value.backup_retention_period
  backup_window              = each.value.backup_window
  maintenance_window         = each.value.maintenance_window
  deletion_protection        = each.value.deletion_protection
  tags                       = each.value.tags
} 