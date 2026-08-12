# Retrieve caller config to get SPN object id dynamically
data "azurerm_client_config" "current" {}

locals {
  spn_object_id = data.azurerm_client_config.current.object_id
}

# ── Azure Resource Group ──────────────────────────────────────────────────────
resource "azurerm_resource_group" "main" {
  name     = var.resource_group_name
  location = var.capacity_location
}

# ── Fabric Capacity (Azure resource) ──────────────────────────────────────────
resource "azurerm_fabric_capacity" "main" {
  name                = var.capacity_name
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location

  administration_members = [
    local.spn_object_id,
    var.admin_user_upn
  ]

  sku {
    name = var.capacity_sku_size
    tier = "Fabric"
  }
}

# ── Fabric Capacity datasource (resolves Azure id → Fabric GUID) ───────────────
data "fabric_capacity" "main" {
  display_name = var.capacity_name
  depends_on   = [azurerm_fabric_capacity.main]
}

# ── Fabric Workspace ──────────────────────────────────────────────────────────
resource "fabric_workspace" "main" {
  display_name = var.workspace_name
  capacity_id  = data.fabric_capacity.main.id
  depends_on   = [data.fabric_capacity.main]
}

# ── Workspace Role Assignments ────────────────────────────────────────────────

# Grant the service principal Admin access so it can run CI/CD automation
resource "fabric_workspace_role_assignment" "spn_admin" {
  workspace_id = fabric_workspace.main.id
  principal = {
    id   = var.spn_object_id
    type = "ServicePrincipal"
  }
  role = "Admin"
}

# Grant an admin security group Admin access (skip if admin_group_id is empty)
resource "fabric_workspace_role_assignment" "admin_group" {
  count        = var.admin_group_id != "" ? 1 : 0
  workspace_id = fabric_workspace.main.id
  principal = {
    id   = var.admin_group_id
    type = "Group"
  }
  role = "Admin"
}

# Grant the dev team Member access (skip if dev_group_id is empty)
resource "fabric_workspace_role_assignment" "dev_group" {
  count        = var.dev_group_id != "" ? 1 : 0
  workspace_id = fabric_workspace.main.id
  principal = {
    id   = var.dev_group_id
    type = "Group"
  }
  role = "Member"
}
