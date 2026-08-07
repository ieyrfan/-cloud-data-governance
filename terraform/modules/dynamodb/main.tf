resource "aws_dynamodb_table" "classification_results" {
  name         = var.table_name
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "resource_id"
  range_key    = "version_id"

  attribute {
    name = "resource_id"
    type = "S"
  }

  attribute {
    name = "version_id"
    type = "S"
  }

  attribute {
    name = "sensitivity_level"
    type = "S"
  }

  global_secondary_index {
    name            = "SensitivityIndex"
    hash_key        = "sensitivity_level"
    range_key       = "resource_id"
    projection_type = "ALL"
  }

  point_in_time_recovery {
    enabled = true
  }

  tags = {
    Environment = var.environment
    Project     = "DataGovernance"
  }
}
