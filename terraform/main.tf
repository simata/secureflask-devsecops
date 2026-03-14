terraform {
  required_version = ">= 1.5.0"

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.80"
    }
  }
}

provider "azurerm" {
  features {}
}

# --- Resource Group ---
resource "azurerm_resource_group" "main" {
  name     = "rg-${var.project_name}-${var.environment}"
  location = var.azure_region

  tags = {
    project     = var.project_name
    environment = var.environment
    managed_by  = "terraform"
  }
}

# --- Container Registry ---
resource "azurerm_container_registry" "main" {
  name                = "${var.project_name}${var.environment}acr"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  sku                 = "Basic"
  admin_enabled       = false # Security: disable admin account, use managed identity

  tags = azurerm_resource_group.main.tags
}

# --- Log Analytics Workspace (for container monitoring) ---
resource "azurerm_log_analytics_workspace" "main" {
  name                = "law-${var.project_name}-${var.environment}"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  sku                 = "PerGB2018"
  retention_in_days   = 30

  tags = azurerm_resource_group.main.tags
}

# --- Container App Environment ---
resource "azurerm_container_app_environment" "main" {
  name                       = "cae-${var.project_name}-${var.environment}"
  resource_group_name        = azurerm_resource_group.main.name
  location                   = azurerm_resource_group.main.location
  log_analytics_workspace_id = azurerm_log_analytics_workspace.main.id

  tags = azurerm_resource_group.main.tags
}

# --- Container App ---
resource "azurerm_container_app" "api" {
  name                         = "ca-${var.project_name}-api"
  container_app_environment_id = azurerm_container_app_environment.main.id
  resource_group_name          = azurerm_resource_group.main.name
  revision_mode                = "Single"

  template {
    min_replicas = 1
    max_replicas = 3

    container {
      name   = "api"
      image  = "${azurerm_container_registry.main.login_server}/${var.project_name}:latest"
      cpu    = 0.25
      memory = "0.5Gi"

      env {
        name  = "FLASK_DEBUG"
        value = "false"
      }

      env {
        name        = "SECRET_KEY"
        secret_name = "app-secret-key"
      }

      liveness_probe {
        transport = "HTTP"
        path      = "/health"
        port      = var.container_port
      }

      readiness_probe {
        transport = "HTTP"
        path      = "/health"
        port      = var.container_port
      }
    }
  }

  ingress {
    external_enabled = true
    target_port      = var.container_port

    traffic_weight {
      percentage      = 100
      latest_revision = true
    }
  }

  secret {
    name  = "app-secret-key"
    value = "REPLACE_WITH_KEYVAULT_REFERENCE"
  }

  tags = azurerm_resource_group.main.tags
}

# --- INTENTIONALLY INSECURE RESOURCES (for Checkov to flag) ---

# INSECURE: Storage account without encryption and with public access
resource "azurerm_storage_account" "insecure_example" {
  name                     = "${var.project_name}${var.environment}st"
  resource_group_name      = azurerm_resource_group.main.name
  location                 = azurerm_resource_group.main.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
  min_tls_version          = "TLS1_0" # INSECURE — Checkov flags this

  # INSECURE — missing:
  #   - allow_nested_items_to_be_public = false
  #   - network_rules with default_action = "Deny"
  #   - enable_https_traffic_only should be true (default in newer versions)

  tags = azurerm_resource_group.main.tags
}