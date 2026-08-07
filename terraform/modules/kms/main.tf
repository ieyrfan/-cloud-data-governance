data "aws_caller_identity" "current" {}

resource "aws_kms_key" "encryption_key" {
  description             = "Key for ${var.sensitivity_level} data in ${var.environment}"
  deletion_window_in_days = 7
  enable_key_rotation     = true
  rotation_period_in_days = var.rotation_days

  # Basic key policy
  policy = jsonencode({
    Version = "2012-10-17"
    Id      = "key-default-1"
    Statement = [
      {
        Sid    = "Enable IAM User Permissions"
        Effect = "Allow"
        Principal = {
          AWS = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:root"
        }
        Action   = "kms:*"
        Resource = "*"
      }
    ]
  })

  tags = {
    Environment      = var.environment
    SensitivityLevel = var.sensitivity_level
    Project          = "DataGovernance"
  }
}

resource "aws_kms_alias" "key_alias" {
  name          = "alias/data-gov-${lower(var.sensitivity_level)}-${var.environment}"
  target_key_id = aws_kms_key.encryption_key.key_id
}
