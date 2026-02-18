output "s3_bucket" { value = aws_s3_bucket.documents.id }
output "dynamodb_vault" { value = aws_dynamodb_table.vault.name }
output "dynamodb_metadata" { value = aws_dynamodb_table.metadata.name }
output "kms_key_arn" { value = aws_kms_key.vault.arn }
output "opensearch_endpoint" { value = aws_opensearch_domain.vectors.endpoint }
