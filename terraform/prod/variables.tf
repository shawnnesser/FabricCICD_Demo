variable "tenant_id"           { type = string }
variable "client_id"           { type = string }
variable "client_secret"       { type = string; sensitive = true }
variable "subscription_id"     { type = string }
variable "spn_object_id"       { type = string }
variable "admin_user_upn"      { type = string }
variable "admin_group_id"      { type = string; default = "" }

variable "resource_group_name" { type = string; default = "rg-fabric-cicd-prod" }
variable "capacity_location"   { type = string; default = "East US" }
variable "capacity_name"       { type = string; default = "fabriccicdprod" }
variable "capacity_sku_size"   { type = string; default = "F16" }
variable "workspace_name"      { type = string; default = "Product Sales - Prod" }
