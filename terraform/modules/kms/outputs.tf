output "key_arn" {
  value = aws_kms_key.encryption_key.arn
}

output "key_id" {
  value = aws_kms_key.encryption_key.key_id
}
