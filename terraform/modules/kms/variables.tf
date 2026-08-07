variable "environment" {
  description = "Environment name"
  type        = string
}

variable "sensitivity_level" {
  description = "The data sensitivity level for this key (e.g., RESTRICTED, CONFIDENTIAL)"
  type        = string
}

variable "rotation_days" {
  description = "Number of days before key rotation"
  type        = number
  default     = 90
}
