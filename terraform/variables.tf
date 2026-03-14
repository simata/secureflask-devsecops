variable "project_name" {
  description = "Project name used for resource naming"
  type        = string
  default     = "secureflask"
}

variable "environment" {
  description = "Deployment environment"
  type        = string
  default     = "dev"

  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be dev, staging, or prod."
  }
}

variable "container_port" {
  description = "Port the container listens on"
  type        = number
  default     = 8000
}

variable "azure_region" {
  description = "Azure region for deployment"
  type        = string
  default     = "uksouth"
}