output "workspace_id"           { value = fabric_workspace.main.id }
output "workspace_name"         { value = fabric_workspace.main.display_name }
output "workspace_dfs_endpoint" { value = fabric_workspace.main.onelake_endpoints.dfs_endpoint }
output "capacity_id"            { value = data.fabric_capacity.main.id }
