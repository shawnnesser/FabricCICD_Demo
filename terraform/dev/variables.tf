variable "tenant_id" {
  description = "Entra ID tenant ID"
  type        = string
}

variable "client_id" {
  description = "Service principal client ID (App Registration)"
  type        = string
}

variable "client_secret" {
  description = "Service principal client secret"
  type        = string
  sensitive   = true
}

variable "subscription_id" {
  description = "Azure subscription ID (for creating Fabric capacity)"
  type        = string
}

variable "resource_group_name" {
  description = "Azure resource group name"
  type        = string
  default     = "rg-fabric-cicd-dev"
}

variable "capacity_location" {
  description = "Azure region for the Fabric capacity"
  type        = string
  default     = "East US"
}

variable "capacity_name" {
  description = "Fabric capacity name (must be globally unique, lowercase, alphanumeric)"
  type        = string
  default     = "fabriccicddev"
}

variable "capacity_sku_size" {
  description = "Fabric capacity SKU (F2, F4, F8, F16, F32, F64 ...)"
  type        = string
  default     = "F4"
}

variable "workspace_name" {
  description = "Fabric workspace display name"
  type        = string
  default     = "Product Sales - Dev"
}

variable "admin_user_upn" {
  description = "UPN of the admin user to add as capacity administrator (e.g. user@contoso.com)"
  type        = string
}

variable "admin_group_id" {
  description = "Object ID of the Entra ID group to grant workspace Admin role"
  type        = string
  default     = ""
}

variable "dev_group_id" {
  description = "Object ID of the Entra ID group to grant workspace Member role"
  type        = string
  default     = ""
}

variable "spn_object_id" {
  description = "Object ID of the Service Principal (used for workspace access)"
  type        = string
}
