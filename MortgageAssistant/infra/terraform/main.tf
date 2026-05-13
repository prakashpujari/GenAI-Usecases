terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 5.0"
    }
  }
}

provider "aws" {
  region = var.region
}

resource "aws_kms_key" "vault" {
  description             = "Mortgage Assistant vault key"
  deletion_window_in_days = 30
  enable_key_rotation     = true
}

resource "aws_s3_bucket" "documents" {
  bucket = var.s3_bucket_name
}

resource "aws_s3_bucket_server_side_encryption_configuration" "documents" {
  bucket = aws_s3_bucket.documents.id

  rule {
    apply_server_side_encryption_by_default {
      kms_master_key_id = aws_kms_key.vault.arn
      sse_algorithm     = "aws:kms"
    }
  }
}

resource "aws_dynamodb_table" "vault" {
  name         = var.vault_table_name
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "document_id"

  attribute {
    name = "document_id"
    type = "S"
  }

  server_side_encryption {
    enabled     = true
    kms_key_arn = aws_kms_key.vault.arn
  }
}

resource "aws_dynamodb_table" "metadata" {
  name         = var.metadata_table_name
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "document_id"

  attribute {
    name = "document_id"
    type = "S"
  }

  server_side_encryption {
    enabled     = true
    kms_key_arn = aws_kms_key.vault.arn
  }
}

resource "aws_opensearch_domain" "vectors" {
  domain_name    = var.opensearch_domain_name
  engine_version = "OpenSearch_2.13"

  cluster_config {
    instance_type = "t3.small.search"
    instance_count = 1
  }

  ebs_options {
    ebs_enabled = true
    volume_size = 20
  }

  encrypt_at_rest {
    enabled = true
    kms_key_id = aws_kms_key.vault.arn
  }

  node_to_node_encryption {
    enabled = true
  }
}
