# Network Configuration
vpc_id = "vpc-083b29333479262bc"
subnet_id = "subnet-0e2f65f1c4945e22b"

db_instances = {
  agentx_db = {
    db_identifier              = "agentx-db"
    engine                     = "mysql"
    engine_version             = "8.4.7"
    instance_class             = "db.t3.micro"
    allocated_storage          = 10
    storage_type               = "gp2"
    storage_encrypted          = true
    db_name                    = "agentx"
    master_username            = "admin"
    master_password            = "admin12345"
    vpc_security_group_ids     = ["sg-0ecfdb9fb90303f17"]
    create_db_subnet_group     = false
    db_subnet_group_name       = "default-vpc-083b29333479262bc"
    publicly_accessible        = false
    skip_final_snapshot        = true
    backup_retention_period    = 7
    backup_window              = "03:00-04:00"
    maintenance_window         = "sun:04:00-sun:05:00"
    deletion_protection        = false
    tags = {
      Name = "agentx"
      Team = "agentx"
    }
  }
}
