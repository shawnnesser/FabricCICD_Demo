output "workspace_id" {
  description = "Fabric workspace ID (save this as FABRIC_DEV_WORKSPACE_ID)"
  value       = fabric_workspace.main.id
}

output "workspace_name" {
  description = "Fabric workspace display name"
  value       = fabric_workspace.main.display_name
}

output "workspace_dfs_endpoint" {
  description = "OneLake DFS endpoint for the workspace"
  value       = fabric_workspace.main.onelake_endpoints.dfs_endpoint
}

output "capacity_id" {
  description = "Fabric capacity GUID"
  value       = data.fabric_capacity.main.id
}
