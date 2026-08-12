# Fabric CI/CD Demo

A comprehensive, production-pattern demonstration of CI/CD for Microsoft Fabric using **fabric-cicd**, **GitHub Actions**, and **Terraform**. This project provisions and manages three full environments (dev, test, prod) with workspaces, Fabric capacity, ADLS Gen2 storage, Azure Key Vault, and automated deployment pipelines — all driven by a Service Principal.

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Project Structure](#project-structure)
4. [Prerequisites](#prerequisites)
5. [Infrastructure Setup (Terraform)](#infrastructure-setup-terraform)
6. [Service Principal Setup](#service-principal-setup)
7. [Python Virtual Environment](#python-virtual-environment)
8. [Sample Data Upload](#sample-data-upload)
9. [Git & GitHub Setup](#git--github-setup)
10. [Fabric Workspace Git Integration](#fabric-workspace-git-integration)
11. [Building the Fabric Solution](#building-the-fabric-solution)
12. [Parameterization](#parameterization)
13. [GitHub Actions CI/CD Pipelines](#github-actions-cicd-pipelines)
14. [Feature Branch Workflow](#feature-branch-workflow)
15. [Folder-to-Workspace Deployment Pattern](#folder-to-workspace-deployment-pattern)
16. [Environment Reference](#environment-reference)
17. [Troubleshooting](#troubleshooting)
18. [Key Lessons Learned](#key-lessons-learned)

---

## 📋 Overview

This project implements a complete end-to-end CI/CD pipeline for a Fabric solution spanning three environments:
- **dev** → development workspace (F4 capacity)
- **test** → testing workspace (F8 capacity)  
- **prod** → production workspace (F16 capacity)

## 🏗️ Project Structure

```
.
├── .github/workflows/          # GitHub Actions workflows
│   ├── deploy-test.yml         # Deploy to test on merge to test branch
│   └── deploy-prod.yml         # Deploy to prod on merge to main (approval gate)
├── src/
│   ├── deploy.py               # fabric-cicd deployment script
│   └── post_deploy.py          # Post-deploy tasks (variable sets, data pipeline, refresh)
├── terraform/
│   ├── dev/                    # Terraform config for dev environment
│   ├── test/                   # Terraform config for test environment
│   └── prod/                   # Terraform config for prod environment
├── workspace/
│   ├── deploy.yml              # fabric-cicd deployment config
│   ├── parameter.yml           # Parameterization rules (SQL endpoints, URLs)
│   └── [item definitions]/     # Item definitions (lakehouse, notebooks, semantic model, report)
├── scripts/
│   ├── create_spn.ps1          # Create Entra ID Service Principal
│   └── setup_venv.ps1          # Create Python venv at C:\venvs\fabric-cicd-demo\
└── requirements.txt            # Python dependencies
```

## 🚀 Getting Started

### 1. Create a Service Principal

```powershell
.\scripts\create_spn.ps1 -AppName "fabric-cicd-spn" -TenantId "<your-tenant-id>"
```

Save the output values:
- `AZURE_TENANT_ID`
- `AZURE_CLIENT_ID`  
- `AZURE_CLIENT_SECRET`
- `SP_OBJECT_ID`

In the **Fabric Admin Portal**:
1. Enable *"Service principals can use Fabric APIs"* in tenant settings
2. Add the SPN as a Fabric capacity administrator

### 2. Provision Environments with Terraform


## Overview

This project is a complete, production-pattern CI/CD demonstration for **Microsoft Fabric**. It implements a three-environment promotion pipeline (dev → test → prod) where Fabric workspace items such as Lakehouses, Notebooks, Semantic Models, and Reports are version-controlled in GitHub and deployed automatically via GitHub Actions using the `fabric-cicd` Python library.

Everything is provisioned from code:
- **Terraform** manages Azure infrastructure (resource groups, Fabric capacity, ADLS Gen2, Key Vault) and Fabric resources (workspaces, role assignments)
- **GitHub Actions** automates deployment of Fabric item definitions between environments
- **fabric-cicd** handles workspace item deployment and environment parameterization
- **A Service Principal** performs all automation without requiring human credentials

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│  GitHub Repository: FabricCICD_Demo                           │
│                                                                      │
│  branch: dev    ◄──────┐  branch: test  ◄────  branch: main        │
│  (integration)         │  (pre-prod)            (production)        │
│       ▲                │       ▲                      ▲             │
│       │ PR merge       │       │ PR merge             │ PR merge    │
│       │                │       │                      │ + APPROVAL  │
└───────┼────────────────┼───────┼──────────────────────┼─────────────┘
        │                │       │                      │
        │           ┌────┴───────┴──────────────────────┴────┐
        │           │         GitHub Actions                  │
        │           │   deploy-test.yml  deploy-prod.yml      │
        │           │       (fabric-cicd Python library)      │
        │           └─────────────────────────────────────────┘
        │
┌───────┴─────────────────────────────────────────────────────────────┐
│  Feature Branches (feature/*)                                       │
│  Created by developers, connected to feature workspaces             │
└─────────────────────────────────────────────────────────────────────┘

┌──────────────────────┐  ┌──────────────────────┐  ┌──────────────────────┐
│   Dev Workspace      │  │   Test Workspace      │  │   Prod Workspace     │
│   (branch: dev)      │  │   (branch: test)      │  │   (branch: main)     │
│   F4 capacity        │  │   F4 capacity         │  │   F4 capacity        │
│   ADLS: dev/         │  │   ADLS: test/         │  │   ADLS: prod/        │
└──────────────────────┘  └──────────────────────┘  └──────────────────────┘
             │                       │                        │
             └───────────────────────┴────────────────────────┘
                                     │
                    ┌────────────────┴────────────────┐
                    │    Shared Azure Infrastructure   │
                    │  ADLS Gen2: <your-storage-account>        │
                    │  Key Vault: <your-dev-key-vault>          │
                    │  Capacity: <your-fabric-capacity> (F4)     │
                    │  Resource Group: rg-fabric-cicd-dev│
                    └──────────────────────────────────┘
```

---

## Project Structure

```
CICDDemos/
├── .github/
│   └── workflows/
│       ├── deploy-test.yml         # Triggered on push to test branch
│       └── deploy-prod.yml         # Triggered on push to main (with approval gate)
├── data/
│   ├── customers.csv               # Adventure Works customers (30 rows)
│   ├── products.csv                # Adventure Works products (56 rows)
│   ├── sales_orders.csv            # Adventure Works sales orders (47 rows)
│   └── sales_territories.csv       # Sales territories (10 rows)
├── scripts/
│   ├── create_spn.ps1              # Creates the Entra ID Service Principal
│   ├── setup_venv.ps1              # Creates Python venv at C:\venvs\fabric-cicd-demo\
│   └── upload_sample_data.ps1      # Uploads CSVs to all ADLS containers
├── src/
│   ├── deploy.py                   # Main fabric-cicd deployment script
│   └── post_deploy.py              # Post-deploy: variable sets, pipeline runs
├── terraform/
│   ├── dev/
│   │   ├── main.tf                 # Resources: RG, capacity, workspace, storage, KV
│   │   ├── variables.tf            # Variable declarations
│   │   ├── outputs.tf              # Outputs: workspace_id, storage URLs, KV URI
│   │   ├── providers.tf            # azurerm + fabric provider config
│   │   ├── terraform.tfvars        # Actual values (EXCLUDED from Git)
│   │   └── terraform.tfvars.example # Template for tfvars
│   ├── test/                       # Same structure as dev
│   └── prod/                       # Same structure as dev
├── workspace/
│   ├── deploy.yml                  # fabric-cicd config: workspace IDs, item types
│   └── parameter.yml               # Parameterization: URL/endpoint replacement rules
├── .gitignore
├── README.md
└── requirements.txt                # Python: fabric-cicd, azure-identity, python-dotenv
```

---

## Prerequisites

Before starting, ensure you have the following:

| Tool | Version | Purpose |
|------|---------|---------|
| Terraform | >= 1.8 | Infrastructure provisioning |
| Python | >= 3.10 | fabric-cicd deployment scripts |
| Azure CLI | Latest | SPN authentication, storage uploads |
| Git | Any | Version control |
| Microsoft Fabric | — | Target platform (F4+ capacity required) |
| GitHub Account | — | Repository and Actions |
| Azure Subscription | — | For Fabric capacity and Azure resources |
| Entra ID admin access | — | To create Service Principal and assign roles |

**Azure Roles required** on your personal account to set everything up:
- Subscription: `Contributor` + `User Access Administrator`
- Entra ID: Global Administrator or Privileged Role Administrator (to assign Fabric Administrator)

---

## Service Principal Setup

The Service Principal (SPN) is the identity used for all automation. It must be created once and configured with the correct permissions before anything else will work.

### Step 1 — Create the App Registration

```powershell
.\scripts\create_spn.ps1 -AppName "fabric-cicd-spn" -TenantId "<your-tenant-id>"
```

Or manually in the Azure Portal:
1. **Entra ID → App registrations → New registration**
2. Name: `fabric-cicd-spn`, Supported account types: Single tenant
3. Click **Register**
4. Note the **Application (client) ID** and **Directory (tenant) ID**
5. Go to **Certificates & secrets → New client secret**
6. Note the **secret value** (shown only once)

### Step 2 — Get the Enterprise Application Object ID

> **Important:** There are TWO different Object IDs. You need the **Enterprise Application Object ID** (not the App Registration Object ID) for Fabric role assignments.

```powershell
az ad sp show --id <client-id> --query "{appId:appId, objectId:id}" -o table
```

Use the `objectId` field from this output in `spn_object_id` in your `terraform.tfvars`.

### Step 3 — Add API Permissions (Critical)

In the App Registration → **API permissions**:
1. Click **Add a permission → Power BI Service**
2. Choose **Application permissions**
3. Select: ✅ `Tenant.Read.All` and ✅ `Tenant.ReadWrite`
4. Click **Grant admin consent for [your org]**

> **Why this is required:** The Fabric Terraform provider and fabric-cicd library call the Fabric REST API on behalf of the SPN. Without these permissions, all Fabric API calls return `Unauthorized`.

### Step 4 — Assign Azure Roles

```powershell
# Contributor - creates Fabric capacity and Azure resources
az role assignment create --role "Contributor" \
  --assignee "<enterprise-app-object-id>" \
  --scope "/subscriptions/<subscription-id>"

# User Access Administrator (scoped to resource group) - allows Terraform to assign roles
az role assignment create --role "User Access Administrator" \
  --assignee "<enterprise-app-object-id>" \
  --scope "/subscriptions/<subscription-id>/resourceGroups/<rg-name>"
```

### Step 5 — Assign Fabric Administrator Role

In the Azure Portal:
1. Go to **Entra ID → Roles and administrators**
2. Search for **Fabric Administrator**
3. Click **Add assignments → Select member → fabric-cicd-spn**

> This is a directory-level role. It gives the SPN permission to create and manage Fabric workspaces. Without it, workspace creation fails with `Unauthorized`.

### Step 6 — Configure Fabric Admin Portal Tenant Settings

In **Microsoft Fabric → Settings (gear) → Admin portal → Tenant settings → Developer settings**:

| Setting | Value |
|---------|-------|
| Service principals can create workspaces, connections, and deployment pipelines | ✅ **Enabled for the entire organization** |
| Service principals can call Fabric public APIs | ✅ **Enabled** |

> **This is the most commonly missed step.** Even with all roles correctly assigned, workspace creation will fail with `Unauthorized` if these tenant settings are off.

In **Microsoft Fabric → Settings (gear) → Admin portal → Tenant settings → Integration settings**:

| Setting | Value | Purpose |
|---------|-------|---------|
| Users can sync workspace items with their Git repositories (preview) | ✅ **Enabled** | Enables Git integration on any workspace |
| Users can export items to Git repositories in other Git providers (preview) | ✅ **Enabled** | Unlocks the **GitHub** option (without this, only Azure DevOps is available) |

> **Note:** After enabling these settings, allow **5–15 minutes** for propagation before the GitHub option appears in Workspace Settings → Git integration. These settings are completely separate from the Developer settings above.

### Step 7 — Add SPN as Capacity Admin

In **Fabric Admin portal → Capacity settings → [your capacity]**:
- Under **Capacity admins**, add the SPN

---

## Python Virtual Environment

The venv is stored at `C:\venvs\fabric-cicd-demo\` — intentionally **off OneDrive** — to avoid issues with corporate certificate policies that block packages installed in OneDrive-synced directories.

### Setup

```powershell
.\scripts\setup_venv.ps1
```

This creates the venv and installs all dependencies from `requirements.txt`:
- `fabric-cicd >= 1.2.0`
- `azure-identity`
- `microsoft-fabric-api >= 0.1.0b1`
- `python-dotenv`

### Activate in future sessions

```powershell
& 'C:\venvs\fabric-cicd-demo\Scripts\Activate.ps1'
```

---

## Infrastructure Setup (Terraform)

Terraform provisions all Azure and Fabric resources. Each environment (dev, test, prod) has its own Terraform configuration in `terraform/<env>/`.

### Resources Created Per Environment

| Resource | Type | Description |
|---------|------|-------------|
| Resource Group | Azure | `rg-fabric-cicd-dev/test/prod` |
| Fabric Capacity | Azure | F4 SKU (shared for demo; scale per env in prod) |
| Fabric Workspace | Fabric | `Product Sales - Dev/Test/Prod` |
| Workspace Role Assignment | Fabric | SPN granted Admin role |
| ADLS Gen2 Storage Account | Azure | `<your-storage-account>` with dev/test/prod containers |
| Azure Key Vault | Azure | `<your-dev-key-vault>` with secrets |
| Key Vault Secrets | Azure | SPN credentials, tenant ID, storage URLs |

### Setup Steps

**1. Configure terraform.tfvars for each environment**

```powershell
cd terraform\dev
Copy-Item terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars with your actual values
```

Required values in `terraform.tfvars`:

```hcl
tenant_id            = "your-tenant-id"
client_id            = "your-spn-client-id"
client_secret        = "your-spn-client-secret"
subscription_id      = "your-subscription-id"
spn_object_id        = "your-enterprise-app-object-id"  # NOT app registration object id
admin_user_upn       = "admin@yourtenant.onmicrosoft.com"
storage_account_name = "yourstorageaccountname"         # globally unique, no hyphens
key_vault_name       = "yourkeyvaultname"               # globally unique
```

**2. Initialize and apply**

```powershell
# Add terraform to PATH first if needed
$env:Path = "C:\Users\<user>\AppData\Local\Microsoft\WinGet\Packages\Hashicorp.Terraform_Microsoft.Winget.Source_8wekyb3d8bbwe;$env:Path"

cd terraform\dev
terraform init
terraform apply -auto-approve
```

**3. Note the Terraform outputs**

```
workspace_id           = "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
workspace_name         = "Product Sales - Dev"
storage_account_name   = "<your-storage-account>"
storage_dev_url        = "abfss://dev@<your-storage-account>.dfs.core.windows.net"
key_vault_uri          = "https://<your-dev-key-vault>.vault.azure.net/"
```

Save the `workspace_id` values for each environment — needed for GitHub Actions variables and `deploy.yml`.

**4. Repeat for test and prod**

```powershell
cd ..\test && terraform init && terraform apply -auto-approve
cd ..\prod && terraform init && terraform apply -auto-approve
```

### Important Notes on Terraform

- **Fabric capacity must be Active (not Paused)** before workspace creation. If you get `CapacityNotInActiveState`:
  ```powershell
  az rest --method post --url "https://management.azure.com/subscriptions/<sub>/resourceGroups/<rg>/providers/Microsoft.Fabric/capacities/<name>/resume?api-version=2023-11-01"
  ```

- **Provider version:** Uses `microsoft/fabric` v1.8.0 and `hashicorp/azurerm` v4.63.0

- **`storage_use_azuread = true`** is set in the azurerm provider block. This is required when the tenant policy disables storage account key-based authentication.

- **`public_network_access_enabled = true`** is required on both Key Vault and Storage Account resources if the tenant has policies that default to private-only access.

---

## Sample Data Upload

Adventure Works style master/reference data is stored in the `data/` folder and uploaded to all three ADLS containers:

| File | Rows | Description |
|------|------|-------------|
| `customers.csv` | 30 | Customer master with address, contact, company |
| `products.csv` | 56 | Product catalog with category, price, color, size |
| `sales_orders.csv` | 47 | Order header and detail with line totals |
| `sales_territories.csv` | 10 | Territory hierarchy with regional sales YTD |

### Upload Command

```powershell
# Run from the repo root after terraform apply
.\scripts\upload_sample_data.ps1 -StorageAccountName "<your-storage-account>"
```

The script authenticates as the SPN and uploads all CSVs to the `dev`, `test`, and `prod` containers. Each environment gets identical reference data; parameterization controls which container path Fabric notebooks read from.

> **Note:** You may see a warning "The request may be blocked by network rules". This is a cosmetic Azure CLI warning when key-based auth is disabled. Uploads still succeed via OAuth when the SPN has `Storage Blob Data Contributor`.

### Container URLs

| Environment | ABFSS URL |
|-------------|-----------|
| Dev | `abfss://dev@<your-storage-account>.dfs.core.windows.net` |
| Test | `abfss://test@<your-storage-account>.dfs.core.windows.net` |
| Prod | `abfss://prod@<your-storage-account>.dfs.core.windows.net` |

---

## Git & GitHub Setup

### Repository Branches

This project uses three long-lived branches mapping to the three environments:

| Branch | Maps To | Purpose |
|--------|---------|---------|
| `main` | Prod workspace | Production — protected, requires PR + approval |
| `test` | Test workspace | Pre-production validation |
| `dev` | Dev workspace | Integration branch — all features merge here first |

Create them if they don't exist:

```powershell
git checkout -b dev && git push origin dev
git checkout -b test && git push origin test
# main already exists
```

### GitHub Repository Secrets

In your GitHub repository → **Settings → Secrets and variables → Actions → Secrets**:

| Secret Name | Value |
|------------|-------|
| `AZURE_TENANT_ID` | Your Entra ID tenant ID |
| `AZURE_CLIENT_ID` | SPN Application (client) ID |
| `AZURE_CLIENT_SECRET` | SPN client secret |

### GitHub Repository Variables

In **Settings → Secrets and variables → Actions → Variables**:

| Variable Name | Value |
|--------------|-------|
| `FABRIC_TEST_WORKSPACE_ID` | From `terraform output workspace_id` in test env |
| `FABRIC_PROD_WORKSPACE_ID` | From `terraform output workspace_id` in prod env |

### GitHub Environments

In **Settings → Environments**:

1. Create environment `test` (optional: add protection rules)
2. Create environment `prod`:
   - ✅ **Required reviewers** — add yourself or an approval team
   - This creates a manual approval gate before prod deployments

---

## Fabric Workspace Git Integration

Each workspace must be manually connected to its GitHub branch via the Fabric UI. This is a one-time setup per workspace.

### Pre-requisites: Enable GitHub in Fabric Admin Portal

Before GitHub appears as an option, two tenant settings must be enabled in **Fabric Admin Portal → Tenant settings → Integration settings**:

| Setting | Purpose |
|---------|--------|
| Users can sync workspace items with their Git repositories (preview) | Enables Git integration on any workspace |
| Users can export items to Git repositories in other Git providers (preview) | Unlocks the GitHub option (without this only Azure DevOps appears) |

> Allow **5–15 minutes** for propagation after saving before the GitHub option lights up.

### Steps (repeat for each workspace)

1. Open the workspace in **Microsoft Fabric** (https://app.fabric.microsoft.com)
2. Click the workspace name → **Workspace settings**
3. Select **Git integration**
4. Click **Connect to Git** → select **GitHub**
5. Enter your **GitHub Personal Access Token** (PAT) with `repo` scope — create at [github.com/settings/tokens](https://github.com/settings/tokens) → Generate new token (classic)
6. Configure:
   - **Repository:** `FabricCICD_Demo`
   - **Branch:** `dev` (for dev workspace), `test` (for test), `main` (for prod)
   - **Git folder:** `workspace` (no leading slash)
7. Click **Connect and sync** — if prompted "Create a new folder?", click **Create and sync**

### After Connecting

The workspace will sync with the `workspace/` folder in the branch. You can now:
- See uncommitted changes in **Source control** panel
- Commit workspace items to GitHub
- Pull updates from GitHub into the workspace

---

## Workspace Identity (Managed Identity)

Each Fabric workspace has a system-assigned managed identity. This is used to authenticate to ADLS Gen2 from Spark notebooks — **no credentials or Key Vault access required**.

### Enabling Workspace Identity

For each workspace: **Workspace Settings → Workspace identity → Enable workspace identity**

### Provisioned Workspace Identities

| Workspace | Object ID | App ID |
|-----------|-----------|--------|
| Product Sales - Dev | `<your-dev-workspace-identity-object-id>` | `<your-dev-workspace-identity-app-id>` |
| Product Sales - Test | `<your-test-workspace-identity-object-id>` | `<your-test-workspace-identity-app-id>` |
| Product Sales - Prod | `<your-prod-workspace-identity-object-id>` | `<your-prod-workspace-identity-app-id>` |

### RBAC Granted

All three workspace identities have been granted **Storage Blob Data Contributor** on `<your-storage-account>`:

```powershell
$storageId = az storage account show --name <your-storage-account> --query id -o tsv
# Repeat for each workspace identity Object ID:
az role assignment create --role "Storage Blob Data Contributor" \
  --assignee "<workspace-identity-object-id>" --scope $storageId
```

---

## Building the Fabric Solution

Build the Fabric items in the **dev workspace** after connecting it to Git. All items should be created in the `Product Sales - Dev` workspace.

### Items to Create

| Item | Name | Purpose |
|------|------|---------|
| Lakehouse | `DemoDataLake` | Stores tables: customers, products, sales_orders, territories |
| Notebook | `Create Lakehouse Tables` | Reads CSVs from Lakehouse Files and creates lakehouse tables |
| Semantic Model | `DemoDirectLakeSemModel` | DirectLake model over the lakehouse |
| Report | `Sales Dashboard` | Power BI report using the semantic model |

### Notebook Pattern

The checked-in `Create Lakehouse Tables` notebook reads CSVs from the Lakehouse `Files/` area, not directly from ADLS or Key Vault:

**Cell 1 — Configuration**:
```python
print("Reading from Lakehouse Files/ ✓")
```

**Cell 2 — Load tables**:
```python
tables = ["customers", "products", "sales_orders", "sales_territories"]

for table_name in tables:
  print(f"Loading {table_name}...")
  df = spark.read.option("header", True).option("inferSchema", True).csv(f"Files/{table_name}.csv")
  df.write.format("delta").mode("overwrite").saveAsTable(table_name)
  print(f"  ✓ {table_name}: {df.count()} rows")

print("\nAll tables loaded successfully!")
```

> **Critical:** The notebook metadata still carries the source workspace's `default_lakehouse` and `default_lakehouse_workspace_id` values when committed from dev. Those two GUIDs must be parameterized during promotion or the notebook can deploy successfully to Test but still remain bound to the Dev lakehouse context.

### Committing Items to GitHub

1. In the workspace, open the **Source control** panel (Git icon in top right)
2. You will see all items listed as "New" or "Modified"
3. Add a commit message and click **Commit**

Item definitions are saved to `workspace/` in the `dev` branch as folders like:
```
workspace/
├── sales.Lakehouse/
├── Create Lakehouse Tables.Notebook/
├── Product Sales Model.SemanticModel/
└── Sales Dashboard.Report/
```

---

## Parameterization

Parameterization allows a single item definition to be deployed to multiple environments with environment-specific values automatically substituted.

### How It Works

`workspace/parameter.yml` defines find-and-replace rules. During deployment, `fabric-cicd` applies these rules to item definitions before pushing them to the target workspace.

### parameter.yml Structure

```yaml
find_replace:
  # Replace the Lakehouse SQL endpoint (workspace-specific)
  - find_value: 'Sql\.Database\("([^"]*\.datawarehouse\.fabric\.microsoft\.com)[^"]*"'
    replace_value:
      _ALL_: $items.Lakehouse.DemoDataLake.$sqlendpoint
    is_regex: "true"
    item_type: ["SemanticModel"]

  # Rebind the notebook's default Lakehouse to the deployed target item
  - find_value: "<dev-lakehouse-guid>"
    replace_value:
      _ALL_: $items.Lakehouse.DemoDataLake.$id
    item_type: ["Notebook"]
    item_name: "Create Lakehouse Tables"

  # Rebind the notebook's default Lakehouse workspace id
  - find_value: "<dev-workspace-guid>"
    replace_value:
      _ALL_: $workspace.$id
    item_type: ["Notebook"]
    item_name: "Create Lakehouse Tables"
```

### deploy.yml Structure

```yaml
core:
  workspace_id:
    test: "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"   # from terraform output
    prod: "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"   # from terraform output
  repository_directory: "."
  item_types_in_scope:
    - Lakehouse
    - Notebook
    - DataPipeline
    - SemanticModel
    - Report
    - VariableLibrary
  parameter: parameter.yml
```

---

## GitHub Actions CI/CD Pipelines

### GitHub Environments Setup

GitHub Environments gate deployments and can enforce approval rules. You need exactly **two** environments — `test` and `prod`. **Dev does not get an environment** because there is no automated deployment to dev; developers work directly in the dev workspace and commit via Fabric's Source Control UI.

Create environments at: **Settings → Environments → New environment**

| Environment | Name | Protection rules |
|-------------|------|-----------------|
| Test | `test` | None required — deploys automatically on PR merge |
| Prod | `prod` | Optional: add yourself as a required reviewer for a manual approval gate |

> **Why no `dev` environment?** The dev workflow is: build in Fabric UI → commit to `dev` branch via Source Control panel → open PR to `test`. GitHub Actions only triggers on merges to `test` and `main`, never on `dev`.

The promotion flow:
```
Dev workspace     PR: dev→test      PR: test→main
(manual work)  →  (auto-deploy)  →  (auto-deploy)
```

### How to Create the GitHub Actions YAML Files

GitHub Actions workflows are just YAML files stored under `.github/workflows/`. Each file becomes an action in the GitHub **Actions** tab as soon as it is committed and pushed to the repository.

For this project, create two workflow files:

| File | Purpose | Trigger |
|------|---------|---------|
| `.github/workflows/deploy-test.yml` | Deploys Fabric items to the Test workspace | Push or PR merge into `test` |
| `.github/workflows/deploy-prod.yml` | Deploys Fabric items to the Prod workspace | Push or PR merge into `main` |

Basic process:

1. In the repository, create the folder `.github/workflows` if it does not already exist.
2. Add a workflow YAML file such as `deploy-test.yml`.
3. Give the workflow a `name`; this is what appears in the GitHub Actions UI.
4. Add an `on` block to define when it runs.
5. Add one or more `jobs` that run on a GitHub-hosted runner such as `ubuntu-latest`.
6. Add `steps` to check out the repo, install Python dependencies, and run the deployment scripts.
7. Commit and push the YAML file. GitHub automatically creates the action from the file.

Minimal pattern used by this repo:

```yaml
name: Deploy to Test

on:
  push:
    branches:
      - test
  workflow_dispatch:

jobs:
  deploy-test:
    runs-on: ubuntu-latest
    environment: test

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Deploy Fabric solution
        env:
          AZURE_TENANT_ID: ${{ secrets.TENANT_ID }}
          AZURE_CLIENT_ID: ${{ secrets.CLIENT_ID }}
          AZURE_CLIENT_SECRET: ${{ secrets.CLIENT_SECRET }}
        run: python src/deploy.py --environment test

      - name: Run post-deploy tasks
        env:
          AZURE_TENANT_ID: ${{ secrets.TENANT_ID }}
          AZURE_CLIENT_ID: ${{ secrets.CLIENT_ID }}
          AZURE_CLIENT_SECRET: ${{ secrets.CLIENT_SECRET }}
          FABRIC_TEST_WORKSPACE_ID: "<your-test-workspace-id>"
        run: python src/post_deploy.py --environment test
```

Key YAML sections:

| Section | What it does |
|---------|--------------|
| `name` | Display name in the GitHub Actions tab |
| `on` | Trigger rules, such as push to `test`, push to `main`, or manual run |
| `workflow_dispatch` | Adds the **Run workflow** button in GitHub |
| `jobs` | Groups the work GitHub will run |
| `runs-on` | Chooses the runner image, such as `ubuntu-latest` |
| `environment` | Connects the job to a GitHub Environment such as `test` or `prod` |
| `steps` | Ordered commands/actions that perform checkout, setup, deploy, and post-deploy |
| `secrets.*` | Pulls sensitive values from GitHub repository secrets |
| `vars.*` | Pulls non-secret configuration values from GitHub repository variables |

For Prod, copy the Test workflow and change:

| Test value | Prod value |
|------------|------------|
| `name: Deploy to Test` | `name: Deploy to Prod` |
| branch `test` | branch `main` |
| job name `deploy-test` | job name `deploy-prod` |
| `environment: test` | `environment: prod` |
| `--environment test` | `--environment prod` |
| `FABRIC_TEST_WORKSPACE_ID` | `FABRIC_PROD_WORKSPACE_ID` |

After creating the YAML files, finish setup in GitHub:

1. Go to **Settings → Secrets and variables → Actions → Secrets** and add `TENANT_ID`, `CLIENT_ID`, and `CLIENT_SECRET`.
2. Go to **Settings → Secrets and variables → Actions → Variables** and add workspace IDs such as `FABRIC_PROD_WORKSPACE_ID` if the workflow references them.
3. Go to **Settings → Environments** and create `test` and `prod`.
4. On the `prod` environment, optionally add required reviewers for a manual approval gate.
5. Go to the **Actions** tab and confirm `Deploy to Test` and `Deploy to Prod` appear.
6. Use **Run workflow** for a manual test, or merge into the target branch to trigger the deployment automatically.

Related project YAML files:

| File | Purpose |
|------|---------|
| `workspace/deploy.yml` | Tells `fabric-cicd` which workspace IDs, item types, and parameter file to use |
| `workspace/parameter.yml` | Defines environment-specific replacements, such as SQL endpoints and Lakehouse bindings |
| `.github/workflows/deploy-test.yml` | Tells GitHub how to deploy to Test |
| `.github/workflows/deploy-prod.yml` | Tells GitHub how to deploy to Prod |

### Required GitHub Secrets

Add at **Settings → Secrets and variables → Actions → Secrets**:

| Secret name | Value |
|------------|-------|
| `TENANT_ID` | `<your-tenant-id>` |
| `CLIENT_ID` | `<your-client-id>` |
| `CLIENT_SECRET` | SPN client secret (from `terraform/dev/terraform.tfvars`) |

### deploy-test.yml

**Trigger:** Push or merge to `test` branch

```yaml
on:
  push:
    branches: [test]
```

**Steps:**
1. Checkout repository
2. Set up Python 3.11
3. Install dependencies: `pip install -r requirements.txt`
4. **Deploy items:** `python src/deploy.py --environment test` — uses `fabric-cicd` (`FabricWorkspace` + `publish_all_items`) to deploy Lakehouse schema, Notebook definitions, and Semantic Model into the Test workspace
5. **Post-deploy:** `python src/post_deploy.py --environment test` — uploads CSV data files into the Test Lakehouse via OneLake API, then triggers the `Create Lakehouse Tables` notebook to load delta tables

### deploy-prod.yml

**Trigger:** Push or merge to `main` branch  
**Gate:** Requires approval from designated reviewers (configured in GitHub Environments)

```yaml
on:
  push:
    branches: [main]
environment: prod   # Triggers approval gate
```

### Running Manually

```powershell
# Activate venv
& 'C:\venvs\fabric-cicd-demo\Scripts\Activate.ps1'

# Set environment variables
$env:AZURE_TENANT_ID     = "your-tenant-id"
$env:AZURE_CLIENT_ID     = "your-client-id"
$env:AZURE_CLIENT_SECRET = "your-client-secret"
$env:FABRIC_TEST_WORKSPACE_ID = "test-workspace-id"

# Deploy
python src/deploy.py --environment test
python src/post_deploy.py --environment test
```

---

## Feature Branch Workflow

Feature branches allow individual developers to work in isolation without affecting the integration (dev) environment.

### GUI-First Developer Steps

You can do this flow entirely graphically using Fabric and GitHub in the browser.

1. In GitHub, open the repository and switch to the `dev` branch.
2. Use the branch selector to create a new branch from `dev`.
  - Example branch name: `feature/my-new-report`
3. In Fabric, create a new workspace.
  - Example workspace name: `Product Sales - Feature/my-new-report`
4. In that new workspace, open **Workspace settings** → **Git integration** / **Source control**.
5. Connect the workspace to:
  - repository: this GitHub repo
  - branch: `feature/my-new-report`
  - folder: `/workspace`
6. Build or modify Fabric items in the feature workspace.
7. In the feature workspace, open **Source control** and commit the changes.
8. In GitHub, create a pull request with:
  - `base: dev`
  - `compare: feature/my-new-report`
9. Merge the PR into `dev`.
10. After merge, you can delete the feature workspace if it is no longer needed.

### Optional CLI Equivalent

If you prefer the terminal for branch creation, the equivalent commands are:

```powershell
git checkout dev
git pull origin dev
git checkout -b feature/my-new-report
git push origin feature/my-new-report
```

### Notes

- The feature workspace should point to the feature branch, not `dev`.
- The Git folder should remain `/workspace`.
- Do not promote feature branches directly to `test`; merge them into `dev` first.

### Integration → Test → Prod Promotion

```
dev  ──PR──►  test  ──PR──►  main (prod)
                               │
                          Requires approval
                          from designated
                          reviewers
```

Each PR merge triggers the corresponding GitHub Actions workflow. The `parameter.yml` rules automatically swap environment-specific values (storage URLs, SQL endpoints) during deployment.

Use these exact PR selections for promotions:

- Dev to Test: `base: test`, `compare: dev`
- Test to Prod: `base: main`, `compare: test`

Recommended promotion order for this repo:

1. Feature branch → `dev`
2. `dev` → `test`
3. `test` → `main`

---

## Folder-to-Workspace Deployment Pattern

Some customers prefer to develop multiple solutions in folders inside one shared Dev workspace, while deploying each folder into its own dedicated Test and Prod workspaces. This can be implemented with folder-aware deployment automation.

> **Important:** A Fabric folder is an organizational boundary, not an automatic deployment boundary. The deployment configuration and scripts must explicitly map each source folder to its target workspaces.

### Example Architecture

```text
Shared Dev workspace
├── Sales
├── Finance
└── Operations

Sales folder      → Sales Test workspace      → Sales Prod workspace
Finance folder    → Finance Test workspace    → Finance Prod workspace
Operations folder → Operations Test workspace → Operations Prod workspace
```

The Git repository remains the source of truth. Each top-level solution folder should have a corresponding repository directory:

```text
workspace/
├── Sales/
│   ├── parameter.yml
│   └── Fabric item definitions
├── Finance/
│   ├── parameter.yml
│   └── Fabric item definitions
└── Operations/
    ├── parameter.yml
    └── Fabric item definitions
```

### Recommended Routing Configuration

Maintain one version-controlled deployment manifest that records the relationship between source folders and target workspaces. For example:

```yaml
solutions:
  sales:
    repository_directory: workspace/Sales
    item_types:
      - Lakehouse
      - Notebook
      - SemanticModel
      - Report
    workspace_variables:
      test: SALES_TEST_WORKSPACE_ID
      prod: SALES_PROD_WORKSPACE_ID

  finance:
    repository_directory: workspace/Finance
    item_types:
      - Warehouse
      - Notebook
      - SemanticModel
      - Report
    workspace_variables:
      test: FINANCE_TEST_WORKSPACE_ID
      prod: FINANCE_PROD_WORKSPACE_ID
```

Store the actual workspace IDs as GitHub Environment or repository variables rather than embedding customer workspace IDs in source code. Secrets, credentials, and connection tokens must remain in GitHub secrets or an approved secret store.

### Deployment Flow

The deployment entry point should accept both a solution and an environment:

```text
deploy --solution sales --environment test
deploy --solution finance --environment prod
```

The automation should then:

1. Read the deployment manifest.
2. Validate the requested solution and environment.
3. Select only that solution's repository directory.
4. Resolve the target workspace ID from environment configuration.
5. Apply the solution-specific parameterization rules.
6. Publish only the supported item types from that folder.
7. Run solution-specific post-deployment tasks and smoke tests.
8. Record the solution, commit SHA, target workspace, and deployment result.

The promotion model remains unchanged:

```text
Feature branch → dev → test → main
                         │       │
                         │       └── Deploy each changed folder to its Prod workspace
                         └────────── Deploy each changed folder to its Test workspace
```

### Workflow Guidance

Use path filters so a change to one solution does not unnecessarily deploy every solution:

```yaml
on:
  push:
    branches: [test]
    paths:
      - "workspace/Sales/**"
      - "config/solutions.yml"
      - "src/**"
```

For many solutions, use a reusable workflow or a dynamically generated job matrix. A change-detection job can identify the modified top-level folders and deploy only those solutions. Changes to shared deployment code or the central manifest should trigger validation for every affected solution.

Recommended GitHub Environments include:

```text
sales-test
sales-prod
finance-test
finance-prod
```

This supports independent workspace variables, secrets, reviewers, approval gates, deployment histories, and release schedules.

### Parameterization Requirements

Each solution should own its environment-specific parameterization. Common values that must be replaced during deployment include:

- Workspace IDs
- Lakehouse and Warehouse IDs
- SQL endpoints
- Connection and gateway IDs
- Notebook default Lakehouse bindings
- Pipeline and notebook references
- Semantic model data sources
- Environment-specific URLs and storage locations

Never assume that an item ID created in the shared Dev workspace will be valid in a dedicated Test or Prod workspace.

### Dependency Boundaries

Keep dependencies within the same solution folder whenever possible:

```text
Recommended: Sales Report → Sales Semantic Model → Sales Lakehouse
Avoid:       Sales Report → Finance Semantic Model
```

If cross-solution dependencies are required, document them as explicit contracts. The deployment process must then include dependency ordering, target item discovery, ID rebinding, compatibility validation, and failure handling.

### Target Workspace Source Control

When `fabric-cicd` or another API-based process deploys to Test and Prod, consider leaving those target workspaces disconnected from Git. This provides one authoritative synchronization path:

```text
Git repository → GitHub Actions → deployment automation → target workspace
```

Connecting a target workspace to Git while also deploying through APIs can create competing synchronization mechanisms and confusing source-control drift. If target workspace Git integration is required, define which mechanism owns updates and prohibit direct edits in Test and Prod.

### Deletion and Ownership Safety

A folder-scoped deployment must never delete items owned by another solution. Before enabling deletion synchronization:

1. Define which solution owns each deployed item.
2. Scope deletion checks to that solution's target workspace and deployment inventory.
3. Protect shared items from automatic deletion.
4. Test deletion behavior in a non-production workspace.
5. Require approval for destructive Prod operations.

Start with non-destructive publishing until ownership and deletion behavior are fully validated.

### Post-Deployment Recommendations

Allow each solution to define optional post-deployment tasks, such as:

- Creating or updating environment-specific connections
- Assigning workspace roles
- Rebinding notebooks, reports, or semantic models
- Triggering notebooks and pipelines
- Refreshing semantic models
- Running data-quality and smoke tests
- Confirming that required items and dependencies exist

Post-deployment failures should fail the workflow and prevent further promotion.

### Governance Considerations

A shared Dev workspace is appropriate when teams benefit from a common development experience and can accept shared permissions, capacity, naming, and operational risk. Prefer separate Dev workspaces as well when teams require:

- Independent access control or regulatory boundaries
- Capacity and performance isolation
- Conflicting item names
- Independent release schedules
- Strong protection from changes made by other teams

### Customer Implementation Checklist

1. Define one top-level Dev folder per deployable solution.
2. Provision dedicated Test and Prod workspaces for each solution.
3. Create a version-controlled folder-to-workspace deployment manifest.
4. Store workspace IDs in GitHub Environment or repository variables.
5. Give the deployment service principal access to every target workspace.
6. Add solution and environment inputs to the deployment entry point.
7. Create solution-specific parameterization and post-deployment rules.
8. Use path filtering or change detection to deploy only affected folders.
9. Add independent approval gates for each Prod workspace.
10. Define cross-solution dependencies and deployment ordering.
11. Prevent direct edits and uncontrolled Git synchronization in Test and Prod.
12. Validate ownership before enabling automated deletion.

This pattern provides a convenient shared Dev workspace while preserving independently governed Test and Prod workspaces for each customer solution.

---

## Environment Reference

### Provisioned Resources (as of 2026-07-30)

| Resource | Name | ID / URL |
|---------|------|----------|
| Azure Resource Group | `rg-fabric-cicd-dev` | Central US |
| Fabric Capacity | `<your-fabric-capacity>` (F4) | `<your-capacity-id>` |
| Dev Workspace | `Product Sales - Dev` | `<your-dev-workspace-id>` |
| Test Workspace | `Product Sales - Test` | `<your-test-workspace-id>` |
| Prod Workspace | `Product Sales - Prod` | `<your-prod-workspace-id>` |
| Storage Account | `<your-storage-account>` | ADLS Gen2, Central US |
| Key Vault (dev) | `<your-dev-key-vault>` | `https://<your-dev-key-vault>.vault.azure.net/` |
| Key Vault (test) | `<your-dev-key-vault>test` | `https://<your-dev-key-vault>test.vault.azure.net/` |
| Key Vault (prod) | `<your-dev-key-vault>prod` | `https://<your-dev-key-vault>prod.vault.azure.net/` |

### Workspace Identities (Managed Identities)

| Workspace | Object ID | App ID |
|-----------|-----------|--------|
| Product Sales - Dev | `<your-dev-workspace-identity-object-id>` | `<your-dev-workspace-identity-app-id>` |
| Product Sales - Test | `<your-test-workspace-identity-object-id>` | `<your-test-workspace-identity-app-id>` |
| Product Sales - Prod | `<your-prod-workspace-identity-object-id>` | `<your-prod-workspace-identity-app-id>` |

All three identities have **Storage Blob Data Contributor** on `<your-storage-account>`.

### Key Vault Secrets

| Secret Name | Contains |
|------------|---------|
| `spn-client-id` | SPN Application (client) ID |
| `spn-client-secret` | SPN client secret |
| `tenant-id` | Entra ID tenant ID |
| `storage-account-name` | ADLS Gen2 account name |
| `storage-dev-url` | Dev container ABFSS URL |
| `storage-test-url` | Test container ABFSS URL |
| `storage-prod-url` | Prod container ABFSS URL |

### Service Principal

| Property | Value |
|---------|-------|
| Display Name | `fabric-cicd-spn` |
| Application (Client) ID | `<your-client-id>` |
| Enterprise App Object ID | `<your-enterprise-app-object-id>` |
| Tenant ID | `<your-tenant-id>` |
| Azure Roles | Contributor, User Access Administrator (on RG), Storage Blob Data Contributor |
| Entra Roles | Fabric Administrator |
| API Permissions | Power BI Service: Tenant.Read.All, Tenant.ReadWrite (Application, admin consented) |

---

## Troubleshooting

### Workspace creation fails with `Unauthorized`

**Cause:** One or more of the following is missing:
1. Fabric Admin Portal → Developer settings → "Service principals can create workspaces" is **disabled**
2. App Registration is missing Power BI Service API permissions (Tenant.Read.All, Tenant.ReadWrite)
3. Admin consent was not granted for the API permissions
4. Fabric Administrator role not assigned to the SPN in Entra ID

**Fix:** Check all four items in [Service Principal Setup](#service-principal-setup) above.

---

### `CapacityNotInActiveState` error during Terraform apply

**Cause:** Fabric capacities auto-pause after a period of inactivity to save cost.

**Fix:**
```powershell
az rest --method post --url "https://management.azure.com/subscriptions/<sub>/resourceGroups/<rg>/providers/Microsoft.Fabric/capacities/<name>/resume?api-version=2023-11-01"
# Wait ~20 seconds, then re-run terraform apply
```

---

### `PrincipalNotFound` when creating workspace role assignment

**Cause:** Using the App Registration Object ID instead of the Enterprise Application Object ID.

**Fix:** Get the correct object ID:
```powershell
az ad sp show --id <client-id> --query "id" -o tsv
```
Use this value for `spn_object_id` in `terraform.tfvars`.

---

### `PrincipalAlreadyHasWorkspaceRolePermissions` error

**Cause:** Fabric automatically grants the creating SPN Admin access to any workspace it creates. Terraform then tries to create the same role assignment.

**Fix:** Import the existing role assignment into Terraform state:
```powershell
terraform import "fabric_workspace_role_assignment.spn_admin" "<workspace-id>/<spn-object-id>"
```

---

### `KeyBasedAuthenticationNotPermitted` on storage account

**Cause:** Tenant Azure Policy disables storage account key authentication on all new accounts.

**Fix:** Add to the `azurerm_storage_account` resource:
```hcl
shared_access_key_enabled       = false
default_to_oauth_authentication = true
```
And add to the `azurerm` provider block:
```hcl
storage_use_azuread = true
```

---

### `ForbiddenByConnection` when writing Key Vault secrets

**Cause:** Tenant Azure Policy uses a `Modify` effect to force `public_network_access_enabled = false` on Key Vaults asynchronously after creation. Even after Terraform sets it to `true`, the policy reverts it within seconds — blocking the CLI data plane endpoint (`vault.azure.net`).

**Fix:** Use the ARM control plane instead of the data plane. `Microsoft.KeyVault/vaults/secrets` is an ARM resource type that routes through `management.azure.com`, which the policy does not block:
```powershell
# scripts/populate_keyvault_secrets.ps1 uses this approach automatically
.\scripts\populate_keyvault_secrets.ps1 -KeyVaultName "<your-dev-key-vault>"
```

> **Note:** `az keyvault secret set` and `azurerm_key_vault_secret` both use the data plane and will fail. The ARM deployment approach (`az deployment group create` with `Microsoft.KeyVault/vaults/secrets` resources) works reliably even when public network access is disabled.

---

### Storage blob upload warnings ("request may be blocked by network rules")

**Cause:** Azure CLI shows this cosmetic warning for any 403/connection-related issue on ADLS Gen2 when key auth is disabled. The upload may still succeed via OAuth.

**Fix:** Verify uploads actually worked:
```powershell
az storage blob list --account-name <name> --container-name dev --auth-mode login
```
If this also fails, ensure the SPN has `Storage Blob Data Contributor` role and wait ~5 minutes for RBAC propagation.

---

### GitHub option greyed out in Workspace Settings → Git integration

**Cause:** Two separate tenant settings in the Fabric Admin Portal must be enabled — missing the second one leaves GitHub unavailable even when Git integration itself is on.

**Fix:** Go to **Fabric Admin Portal → Tenant settings → Integration settings** and enable both:
1. **"Users can sync workspace items with their Git repositories (preview)"**
2. **"Users can export items to Git repositories in other Git providers (preview)"** ← this is the one that unlocks GitHub

Wait 5–15 minutes after saving for the setting to propagate, then refresh the Workspace Settings page.

---

### `AuthorizationFailed: does not have authorization to perform roleAssignments/write`

**Cause:** SPN has `Contributor` but not `User Access Administrator`, so it cannot create role assignments for other resources.

**Fix:** Grant the SPN `User Access Administrator` scoped to the resource group:
```powershell
az role assignment create \
  --role "User Access Administrator" \
  --assignee "<enterprise-app-object-id>" \
  --scope "/subscriptions/<sub>/resourceGroups/<rg-name>"
```

---

### Reset Test workspace and redeploy everything from Git

If Test gets out of sync and you want to force it back to the current `test` branch state, use one of these runbooks.

#### Option A (recommended): Soft reset in-place

Use this when you want to keep the same Test workspace ID and quickly republish all items.

1. In Fabric, open **Product Sales - Test** workspace.
2. Delete promoted items you want to reset (report, notebook(s), semantic model, lakehouse) in dependency-safe order.
3. In GitHub, open **Actions** and run `Deploy to Test` (manual workflow dispatch), or merge a PR into `test`.
4. Wait for `.github/workflows/deploy-test.yml` to finish successfully.
5. Refresh the Test workspace in Fabric and verify items are present.
6. Verify post-deploy data load results in the Test lakehouse under `Tables/dbo`.

Notes:

- This is the fastest demo-safe reset.
- Deleting items first helps remove drift that simple overwrite deploys may not clean up.

#### Option B: Hard reset (recreate Test workspace)

Use this only when you need a completely fresh Test workspace identity.

1. Recreate Test infrastructure with Terraform in `terraform/test`.
2. Capture the new `workspace_id` from Terraform outputs.
3. Update workspace ID references used by deployment code:
   - `src/deploy.py` (`WORKSPACE_IDS["test"]`)
   - `src/post_deploy.py` (`WORKSPACE_IDS["test"]`)
   - `workspace/deploy.yml` (if you are using config-driven workspace IDs)
4. Commit those ID updates.
5. Trigger Test deployment from Git (`deploy.py` + `post_deploy.py` via workflow or manual run).
6. Refresh Test in Fabric and validate items/tables.

Notes:

- If you recreate Test but do not update IDs, deployment will still target the old workspace.
- Hard reset is slower and usually unnecessary for demos.

#### Quick validation checklist after either reset

1. In Test workspace, confirm expected items exist (Report, Lakehouse, Notebooks, Semantic Model).
2. In Lakehouse, confirm `Files/` has CSVs and `Tables/dbo` has populated tables.
3. In GitHub, confirm the latest `Deploy to Test` workflow run is green.

---

## Key Lessons Learned

These are hard-won insights from building this demo that aren't obvious from documentation:

1. **Two Object IDs exist for every SPN** — The App Registration Object ID and the Enterprise Application Object ID are different. Fabric role assignments require the Enterprise Application Object ID. Get it with `az ad sp show --id <client-id> --query "id"`.

2. **Fabric Admin Portal tenant settings are separate from Entra roles** — Having Fabric Administrator in Entra ID is not enough. The specific tenant settings in the Fabric Admin Portal must also be enabled for SPNs to create workspaces and call APIs.

3. **API permissions on the App Registration are mandatory** — The Fabric Terraform provider and fabric-cicd call the Fabric REST API using the SPN's token. The token must have Power BI Service application permissions or all calls return `Unauthorized`.

4. **Fabric capacity must be Active** — Capacities auto-pause. Any Terraform apply that creates or modifies workspace resources will fail if the capacity is paused. Build a resume step into your workflow if you run applies infrequently.

5. **Tenant Azure Policies silently override Terraform** — On Microsoft 365 demo tenants, policies may disable public network access on storage accounts and Key Vaults immediately after creation. Always explicitly set `public_network_access_enabled = true` and `storage_use_azuread = true` to counteract this.

6. **`User Access Administrator` is needed for RBAC-in-Terraform** — `Contributor` alone cannot create role assignments. Without `User Access Administrator`, any `azurerm_role_assignment` resource in Terraform will fail. Scope it to the resource group to limit blast radius.

7. **ADLS Gen2 CLI tooling has misleading error messages** — The "may be blocked by network rules" warning appears for any auth failure, not just network issues. Check the actual exit code and verify with `az storage blob list`.

8. **The venv must not be in OneDrive** — Corporate certificate policies can interfere with pip-installed packages when the venv is inside an OneDrive-synced folder. Always use `C:\venvs\` or another local path.

---

## Resources

- [Microsoft Fabric CI/CD Whitepaper](https://github.com/FabricDevCamp/fabric-cicd-whitepaper)
- [fabric-cicd Library Documentation](https://microsoft.github.io/fabric-cicd/)
- [Terraform microsoft/fabric Provider](https://registry.terraform.io/providers/microsoft/fabric/latest/docs)
- [Terraform hashicorp/azurerm Provider](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs)
- [Fabric REST API Reference](https://learn.microsoft.com/en-us/rest/api/fabric/articles/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Azure Key Vault RBAC](https://learn.microsoft.com/en-us/azure/key-vault/general/rbac-guide)

---

*Built following best practices from the [Fabric CI/CD Whitepaper](https://github.com/FabricDevCamp/fabric-cicd-whitepaper). All infrastructure managed via Terraform. All deployments via GitHub Actions + fabric-cicd.*

---

## AI Assistant Jumpstart Guide

> **This section is written for AI coding assistants (GitHub Copilot, Claude, ChatGPT, etc.) helping a developer replicate this Fabric CI/CD pattern in their own Azure/Fabric environment.**
> It documents every decision, pitfall, and non-obvious requirement discovered during the original build. Follow this guide in order.

---

### What This Project Builds

A fully automated Fabric CI/CD system where:
- Terraform provisions all Azure + Fabric infrastructure
- Git branches map 1:1 to Fabric workspaces (dev/test/prod)
- fabric-cicd Python library deploys Fabric items between environments
- GitHub Actions orchestrates the promotion pipeline with approval gates
- A Service Principal (SPN) performs all automation — no human credentials in any pipeline

---

### Phase 1: Service Principal — Do This Exactly Right

The SPN is the hardest part to get right. Every subsequent failure will trace back to a missed permission here.

**What to create:**
An Entra ID App Registration with a client secret. Use the Enterprise Application Object ID (not the App Registration Object ID) for all Fabric-related assignments.

**Get the correct Object ID:**
```powershell
# Run this AFTER creating the app registration
az ad sp show --id <CLIENT_ID> --query "id" -o tsv
# Use this value (NOT the object ID shown on the App Registration page itself)
```

**Required permissions — ALL of these are needed:**

| Layer | What | How |
|-------|------|-----|
| Azure RBAC | `Contributor` on subscription | `az role assignment create --role Contributor --assignee <OID>` |
| Azure RBAC | `User Access Administrator` scoped to resource group | Required for Terraform to create role assignments |
| Azure RBAC | `Storage Blob Data Contributor` on storage account | Required for ADLS Gen2 data access |
| Entra ID Role | `Fabric Administrator` | Azure Portal → Entra ID → Roles and administrators → Fabric Administrator |
| App Reg API | Power BI Service → `Tenant.Read.All` (Application) | App Registration → API permissions → Add → Power BI Service → Application |
| App Reg API | Power BI Service → `Tenant.ReadWrite` (Application) | Same as above, admin consent required |
| Fabric Admin Portal | "Service principals can create workspaces" → Enabled | fabric.microsoft.com → Settings → Admin portal → Tenant settings → Developer settings |
| Fabric Admin Portal | "Service principals can call Fabric public APIs" → Enabled | Same location |
| Fabric Capacity | Add SPN as Capacity Admin | Fabric Admin portal → Capacity settings → [capacity name] → Capacity admins |

**The two most commonly missed items:**
1. The Fabric Admin Portal tenant settings (easily overlooked — separate from Entra roles)
2. Using the App Registration Object ID instead of the Enterprise Application Object ID

---

### Phase 2: Terraform Provider Configuration

**Required providers:**
```hcl
terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "4.63.0"  # Tested working version
    }
    fabric = {
      source  = "microsoft/fabric"
      version = "1.8.0"   # Use 1.8.0; 1.9.0 has not been tested
    }
  }
}

provider "azurerm" {
  features {}
  tenant_id           = var.tenant_id
  client_id           = var.client_id
  client_secret       = var.client_secret
  subscription_id     = var.subscription_id
  storage_use_azuread = true  # REQUIRED if tenant policy disables key-based storage auth
}

provider "fabric" {
  tenant_id     = var.tenant_id
  client_id     = var.client_id
  client_secret = var.client_secret
  preview       = true  # REQUIRED for fabric_connection resource
}
```

**Key provider facts:**
- `storage_use_azuread = true` makes the azurerm provider use OAuth for storage data plane operations. Without it, Terraform fails on any storage resource if the tenant has disabled key-based auth.
- `preview = true` on the fabric provider unlocks `fabric_connection` and other preview resources.

---

### Phase 3: Known Tenant Policy Issues and Workarounds

Many enterprise/M365 demo tenants have Azure Policies that create friction. Here is every issue encountered and the fix:

#### Issue 1: `KeyBasedAuthenticationNotPermitted` on Storage Account
**Symptom:** `terraform apply` fails when creating storage account secrets or containers.
**Cause:** Tenant policy disables storage account key auth.
**Fix in HCL:**
```hcl
resource "azurerm_storage_account" "main" {
  shared_access_key_enabled       = false
  default_to_oauth_authentication = true
  # ...
}

provider "azurerm" {
  storage_use_azuread = true
  # ...
}
```

#### Issue 2: `ForbiddenByConnection` on Key Vault secrets
**Symptom:** Key Vault is created successfully but writing secrets fails with 403 `ForbiddenByConnection`.
**Cause:** Tenant policy uses a `Modify` effect to force `publicNetworkAccess = Disabled` asynchronously. Even after Terraform sets `public_network_access_enabled = true` (and the apply succeeds), the policy reverts it within seconds. Both `az keyvault secret set` and `azurerm_key_vault_secret` use the Key Vault **data plane** (`vault.azure.net`) which is blocked.
**Fix:** Use the ARM **control plane** instead. `Microsoft.KeyVault/vaults/secrets` is an ARM resource type that routes through `management.azure.com`, bypassing the data plane restriction entirely:
```powershell
# Build an ARM template with all secrets and deploy via ARM
$armTemplate = @{
    '`$schema'     = "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#"
    contentVersion = "1.0.0.0"
    resources      = @(
        @{ type = "Microsoft.KeyVault/vaults/secrets"; apiVersion = "2023-07-01"
           name = "<vault-name>/<secret-name>"; properties = @{ value = "<secret-value>" } }
    )
}
$armTemplate | ConvertTo-Json -Depth 5 | Out-File secrets.json
az deployment group create --resource-group <rg> --template-file secrets.json
```
The `scripts/populate_keyvault_secrets.ps1` script implements this automatically.

#### Issue 3: `AuthorizationFailed` on role assignments
**Symptom:** `azurerm_role_assignment` fails with "does not have authorization to perform roleAssignments/write".
**Cause:** SPN has `Contributor` but not `User Access Administrator`. Contributor cannot assign roles.
**Fix:**
```powershell
az role assignment create --role "User Access Administrator" \
  --assignee "<enterprise-app-object-id>" \
  --scope "/subscriptions/<sub>/resourceGroups/<rg-name>"
# Scope to RG only (not subscription) to limit blast radius
```

#### Issue 4: `CapacityNotInActiveState`
**Symptom:** workspace creation fails with this error even though capacity exists in state.
**Cause:** Fabric capacities auto-pause when idle.
**Fix:** Resume before applying:
```powershell
az rest --method post --url "https://management.azure.com/subscriptions/<sub>/resourceGroups/<rg>/providers/Microsoft.Fabric/capacities/<name>/resume?api-version=2023-11-01"
Start-Sleep -Seconds 20
terraform apply -auto-approve
```

#### Issue 5: `PrincipalAlreadyHasWorkspaceRolePermissions`
**Symptom:** `fabric_workspace_role_assignment` fails because the SPN already has Admin.
**Cause:** Fabric automatically makes the creating SPN an Admin. Terraform then tries to create the same assignment.
**Fix:** Import the existing assignment:
```powershell
terraform import "fabric_workspace_role_assignment.spn_admin" "<workspace-id>/<spn-object-id>"
```

---

### Phase 4: Resource Sequencing

Terraform handles most dependencies automatically via `depends_on` and implicit references, but these ordering constraints are non-obvious:

```
azurerm_resource_group
  └─► azurerm_fabric_capacity
  │     └─► data.fabric_capacity  (data source to resolve Azure ID → Fabric GUID)
  │           └─► fabric_workspace
  │                 └─► fabric_workspace_role_assignment
  └─► azurerm_storage_account
  │     └─► azurerm_storage_container (dev/test/prod)
  └─► azurerm_key_vault
        └─► azurerm_role_assignment (Key Vault Secrets Officer)
              └─► azurerm_key_vault_secret (if tenant allows data plane access)
```

**Critical:** `data.fabric_capacity` must use `depends_on = [azurerm_fabric_capacity.main]` or it will try to read before the capacity exists.

---

### Phase 5: Fabric Workspace to Git Branch Mapping

This is manual — no Terraform resource exists for Fabric workspace Git integration. Do this in the Fabric UI for each workspace:

```
Workspace Settings → Git integration → Connect to GitHub
  Repository: <your-github-repo>
  Branch:     dev   (for dev workspace)
              test  (for test workspace)
              main  (for prod workspace)
  Git folder: /workspace
```

**One repo, multiple branches, same folder path** — this is the correct pattern. Each workspace sees only its branch's version of the items.

---

### Phase 6: fabric_connection Resource (Preview)

`fabric_connection` is a preview resource. The schema is different from what you'd expect. **Exact working schema:**

```hcl
resource "fabric_connection" "adls" {
  display_name      = "AzureDataLakeStorage-ServicePrincipal-CentralUS"
  connectivity_type = "ShareableCloud"          # NOT the connector type
  privacy_level     = "Organizational"

  connection_details = {
    type            = "AzureDataLakeStorage"    # The connector/data source type
    creation_method = "AzureDataLakeStorage"    # Must match exactly — NOT "Manual" or "ServicePrincipal"
    parameters = [                              # parameters is a SET of {name, value} objects
      { name = "path",   value = "https://<storage-account>.dfs.core.windows.net" },
      { name = "server", value = "https://<storage-account>.dfs.core.windows.net" }
      # Both "path" AND "server" are required — error message reveals each missing one
    ]
  }

  credential_details = {
    credential_type       = "ServicePrincipal"  # Required at top level
    single_sign_on_type   = "None"
    connection_encryption = "NotEncrypted"
    # NOTE: skip_test_connection is NOT supported for AzureDataLakeStorage
    # The connection is ALWAYS tested live during creation
    service_principal_credentials = {           # Nested block — not inline fields
      client_id                = var.client_id
      tenant_id                = var.tenant_id
      client_secret_wo         = var.client_secret   # Write-only
      client_secret_wo_version = 1                   # Increment to rotate
    }
  }
}
```

**Known limitation:** On tenants where Azure Policy enforces `public_network_access = Disabled` on storage accounts, this resource will fail. Fabric's ShareableCloud gateway performs a live connectivity test during creation that requires the ADLS endpoint to be publicly reachable, and `skip_test_connection` is not supported. In that case, create the connection manually in Fabric UI (Manage connections and gateways → New connection) or use a VNet data gateway.

---

### Phase 7: Python venv — Keep Off OneDrive

```powershell
# CORRECT: Off OneDrive to avoid certificate policy issues
python -m venv C:\venvs\fabric-cicd-demo

# WRONG: Inside OneDrive-synced folder
python -m venv "C:\Users\<user>\OneDrive\...\venv"
```

Corporate certificate policies applied to OneDrive-synced paths can block pip package installations. Always put the venv in a local path.

---

### Phase 8: GitHub Actions Setup Checklist

```
Repository Secrets:
  AZURE_TENANT_ID       = <tenant-id>
  AZURE_CLIENT_ID       = <spn-client-id>
  AZURE_CLIENT_SECRET   = <spn-client-secret>

Repository Variables:
  FABRIC_TEST_WORKSPACE_ID = <from: terraform output workspace_id in test env>
  FABRIC_PROD_WORKSPACE_ID = <from: terraform output workspace_id in prod env>

Environments:
  test → optional approval rules
  prod → Required reviewers: <your-github-username>
```

**Workflow trigger pattern:**
```yaml
# deploy-test.yml
on:
  push:
    branches: [test]

# deploy-prod.yml
on:
  push:
    branches: [main]
environment: prod  # This line activates the approval gate
```

---

### Replacing Placeholder Values

When adapting this repo to a new environment, replace these values throughout all files:

| Placeholder | Find in | Replace with |
|------------|---------|-------------|
| `<your-tenant-id>` | All `terraform.tfvars` | Your Entra ID tenant ID |
| `<your-client-id>` | All `terraform.tfvars` | Your SPN client ID |
| `<your-enterprise-app-object-id>` | All `terraform.tfvars` | Your Enterprise App object ID |
| `<your-subscription-id>` | All `terraform.tfvars` | Your Azure subscription ID |
| `<your-storage-account>` | `terraform.tfvars`, scripts | Your storage account name (unique) |
| `<your-dev-key-vault>` | `terraform.tfvars`, scripts | Your Key Vault name (unique) |
| `<your-fabric-capacity>` | `terraform.tfvars` | Your capacity name (unique, no hyphens) |
| `admin@yourtenant.onmicrosoft.com` | `terraform.tfvars` | Your admin UPN |
| `<your-dev-workspace-id>` | `workspace/deploy.yml` | Your dev workspace ID |
| `<your-github-org>/FabricCICD_Demo` | GitHub settings, docs | Your GitHub repo |

---

### Quick Validation Commands

Run these to verify each layer is working:

```powershell
# 1. Verify SPN can authenticate
az login --service-principal -u <client-id> -p <secret> --tenant <tenant-id>
az account show

# 2. Verify Fabric capacity state
az rest --method get \
  --url "https://management.azure.com/subscriptions/<sub>/resourceGroups/<rg>/providers/Microsoft.Fabric/capacities/<name>?api-version=2023-11-01" \
  --query "properties.state" -o tsv
# Expected: "Active"

# 3. Verify workspace exists in Fabric
$token = az account get-access-token --resource "https://api.fabric.microsoft.com" --query accessToken -o tsv
Invoke-RestMethod -Uri "https://api.fabric.microsoft.com/v1/workspaces/<workspace-id>" \
  -Headers @{Authorization="Bearer $token"}

# 4. Verify SPN role on workspace
Invoke-RestMethod -Uri "https://api.fabric.microsoft.com/v1/workspaces/<workspace-id>/roleAssignments" \
  -Headers @{Authorization="Bearer $token"} | Select-Object -ExpandProperty value

# 5. Verify Key Vault access
az keyvault secret list --vault-name <kv-name> --query "[].name" -o tsv

# 6. Verify Terraform state is clean
terraform plan -detailed-exitcode
# Exit code 0 = no changes needed (clean state)
```


```powershell
cd terraform\<environment>
copy terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars with your values
terraform init
terraform plan
terraform apply
```

**Note:** Save the `workspace_id` outputs for Step 4.

### 3. Set Up Python Virtual Environment

```powershell
.\scripts\setup_venv.ps1
```

This creates the venv at `C:\venvs\fabric-cicd-demo\` (off OneDrive to avoid certificate issues).

### 4. Connect Dev Workspace to GitHub

In **Fabric (web)**:
1. Go to dev workspace → **Workspace Settings** → **Git integration**
2. Connect to this GitHub repo, branch: `dev`, Git folder: `/workspace`
3. Commit your Lakehouse, Notebooks, Semantic Model, and Report

Item definitions will be created in the `workspace/` folder.

### 5. Update `workspace/deploy.yml`

Replace the placeholder workspace IDs with the actual IDs from Terraform outputs:

```yaml
core:
  workspace_id:
    test: "<ACTUAL_TEST_WORKSPACE_ID>"
    prod: "<ACTUAL_PROD_WORKSPACE_ID>"
```

### 6. Configure GitHub Repository

**Secrets** (Settings → Secrets and variables → Actions → Secrets):
- `AZURE_TENANT_ID`
- `AZURE_CLIENT_ID`
- `AZURE_CLIENT_SECRET`

**Variables** (Settings → Secrets and variables → Actions → Variables):
- `FABRIC_TEST_WORKSPACE_ID`
- `FABRIC_PROD_WORKSPACE_ID`

**Environments** (Settings → Environments):
- Create `test` environment (optional approval)
- Create `prod` environment with **required approvers** for manual approval gates

### 7. Set Up Git Branches

Create branches for your branching strategy:

```powershell
git checkout -b dev
git checkout -b test
git checkout main  # Already exists
```

## 🔄 CI/CD Flow

1. **Development**: Make changes in a feature workspace or directly in the Dev Fabric workspace, then commit them to the matching Git branch.
2. **Integration**: Merge feature work into `dev` to make `dev` the integration branch and source of truth for the Dev workspace.
3. **Testing**: Create a PR from `dev` to `test`; merging it deploys to the Test workspace.
4. **Production**: Create a PR from `test` to `main`; merging it requires approval and deploys to Prod.

### GitHub PR Selections

Use this rule every time:

- `base` = target branch
- `compare` = source branch

Common pull request selections for this repo:

| Scenario | base | compare |
|---------|------|---------|
| Feature branch into integration | `dev` | `feature/my-change` |
| Dev promotion into Test | `test` | `dev` |
| Test promotion into Prod | `main` | `test` |

### Demo Steps: Dev to Test

1. Make the change in the Fabric Dev workspace.
2. Commit it from Fabric Source control into the `dev` branch.
3. In GitHub, create a pull request with `base: test` and `compare: dev`.
4. Confirm the changed Fabric item folders appear in the PR diff under `workspace/`.
5. Merge the PR.
6. Wait for the Test workflow to finish.
7. Refresh the Test Fabric workspace and verify the item appears.

## 📦 Deployment Pipeline

Each GitHub Actions run has two phases:

### Phase 1 — `deploy.py` (Item Definitions)
Uses `fabric-cicd` (`FabricWorkspace` + `publish_all_items`) to deploy Fabric item definitions into the target workspace:
- Lakehouse structure
- Notebook code (with environment parameters substituted via `parameter.yml`)
- Semantic Model definition
- Report definition

```python
from fabric_cicd import FabricWorkspace, publish_all_items

workspace = FabricWorkspace(
    workspace_id="<target-workspace-id>",
    environment="test",            # controls parameter.yml substitutions
    repository_directory="workspace",
    item_type_in_scope=["Lakehouse", "Notebook", "SemanticModel", "Report"],
    token_credential=credential,
)
publish_all_items(workspace)
```

### Phase 2 — `post_deploy.py` (Data Loading)
After items are deployed, loads data into the Lakehouse:

1. **Finds the Lakehouse** in the target workspace by name (`DemoDataLake`)
2. **Uploads CSV files** from `data/` into Lakehouse Files via OneLake DFS API
3. **Triggers the notebook** (`Create Lakehouse Tables`) via Fabric REST API  
4. **Waits for completion** — polls job status every 30s (up to 30 minutes)

> **Note:** `post_deploy.py` uses the Fabric REST API and OneLake DFS API directly (no SDK). This avoids the `microsoft-fabric-api` SDK which has inconsistent API coverage.

> **Local auth note:** `deploy.py` and `post_deploy.py` use `ClientSecretCredential` for CI. For local runs, they now first honor `AZURE_TENANT_ID`, `AZURE_CLIENT_ID`, and `AZURE_CLIENT_SECRET`, and then fall back to Key Vault lookup using your current `az login` session.

## 🔧 Parameterization

The `workspace/parameter.yml` file defines find-and-replace rules for environment-specific settings:

- SQL endpoint connection strings (workspace-specific)
- Azure storage URLs (different per environment)
- Database server names
- Connection strings

Example:
```yaml
find_replace:
  - find_value: 'Sql\.Database\("([^"]*)datawarehouse\.fabric\.microsoft\.com[^"]*"'
    replace_value:
      _ALL_: $items.Lakehouse.sales.$sqlendpoint
    is_regex: "true"
    item_type: ["SemanticModel"]
```

## 📚 Resources

- [Fabric CI/CD Whitepaper](https://github.com/FabricDevCamp/fabric-cicd-whitepaper)
- [fabric-cicd Library](https://microsoft.github.io/fabric-cicd/)
- [Terraform Fabric Provider](https://registry.terraform.io/providers/microsoft/fabric/latest/docs)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)

## ⚠️ Important Notes

- **Virtual environment** is at `C:\venvs\fabric-cicd-demo\` to avoid OneDrive sync issues with certificates
- **terraform.tfvars** is excluded from Git (contains secrets)
- **Secrets in GitHub** are masked in logs
- **Service Principal** must have Admin access on each workspace for CI/CD automation
- **Item dependencies** are automatically rebound via `logicalId` during deployment
- **Local Azure CLI login is not the same as SPN env vars**. REST checks can succeed with `az login`, while `deploy.py` and `post_deploy.py` still need SPN values from env vars or Key Vault.

## 🛠️ Development

To activate the Python venv in future sessions:

```powershell
& 'C:\venvs\fabric-cicd-demo\Scripts\Activate.ps1'
```

To run deployment manually:

```powershell
python src/deploy.py --environment test
python src/post_deploy.py --environment test
```

If local SPN env vars are not set, the scripts will try these Key Vault names by default:

- `dev` → `<your-dev-key-vault>`
- `test` → `<your-dev-key-vault>test`
- `prod` → `<your-dev-key-vault>prod`

Supported secret names for the SPN lookup are:

- `tenant-id`
- `client-id`
- `client-secret`

The caller still needs Key Vault data-plane access to read those secrets.

### Promotion-specific failure mode: notebook deploys, files upload, but tables stay empty

**Symptom:** `post_deploy.py` uploads `customers.csv`, `products.csv`, `sales_orders.csv`, and `sales_territories.csv` into the Test Lakehouse `Files/` area, but `Tables/dbo` remains empty after the notebook run.

**Cause:** The notebook item was promoted without replacing the dev `default_lakehouse` and `default_lakehouse_workspace_id` embedded in `workspace/Create Lakehouse Tables.Notebook/notebook-content.py`.

**Fix:** Add notebook parameterization rules in `workspace/parameter.yml` for both GUIDs. Also ensure the semantic model rule points to the real lakehouse name `DemoDataLake`, not the older example name `sales`.

### Local Key Vault read can fail even when secret writes succeeded

**Symptom:** The local Key Vault fallback returns 403 `Forbidden` while validating Test credentials.

**Cause:** In this tenant, secrets may be populated through the ARM control plane while data-plane reads at `vault.azure.net` are still blocked by network policy or missing Key Vault RBAC/access policy permissions.

**Fix:** If local Key Vault reads fail, either grant the caller `Key Vault Secrets User`/equivalent data-plane read access and allow public access as required by tenant policy, or provide the three SPN values via environment variables for local runs.

---

Built following best practices from the [Fabric CI/CD Whitepaper](https://github.com/FabricDevCamp/fabric-cicd-whitepaper)
