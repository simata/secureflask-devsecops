output "resource_group_name" {
  description = "Name of the resource group"
  value       = azurerm_resource_group.main.name
}

output "container_registry_url" {
  description = "URL of the container registry"
  value       = azurerm_container_registry.main.login_server
}

output "api_url" {
  description = "URL of the deployed API"
  value       = "https://${azurerm_container_app.api.ingress[0].fqdn}"
}