terraform {
  backend "s3" {
    bucket         = "agentx2026"
    key            = "prod_deploy/cloudfront/terraform.tfstate"
    region         = "ap-south-1"
    profile        = "agentx"
    #dynamodb_table = "terraform-state-lock"
    encrypt        = true
  }
} 