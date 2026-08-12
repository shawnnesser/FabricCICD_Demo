# =============================================================================
# Creates an Entra ID App Registration (Service Principal) and grants the
# permissions needed for Fabric CI/CD automation.
#
# Prerequisites:
#   - Az PowerShell module  (Install-Module Az -Scope CurrentUser)
#   - You must be a Global Admin or Application Administrator in the tenant
#   - The SPN must be added as a Fabric Capacity Administrator
#
# Usage:
#   .\create_spn.ps1 -AppName "fabric-cicd-spn" -TenantId "<your-tenant-id>"
# =============================================================================

param(
    [Parameter(Mandatory=$true)]
    [string]$AppName,

    [Parameter(Mandatory=$true)]
    [string]$TenantId
)

# Connect to Azure (interactive login)
Connect-AzAccount -TenantId $TenantId

# Create the App Registration
Write-Host "Creating App Registration: $AppName ..." -ForegroundColor Cyan
$app = New-AzADApplication -DisplayName $AppName

# Create the Service Principal for the app
$sp = New-AzADServicePrincipal -ApplicationId $app.AppId

# Create a client secret (valid for 1 year)
$secretEndDate = (Get-Date).AddYears(1)
$secret = New-AzADAppCredential -ApplicationId $app.AppId -EndDate $secretEndDate

Write-Host ""
Write-Host "======================================================" -ForegroundColor Green
Write-Host "  App Registration created successfully!" -ForegroundColor Green
Write-Host "======================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Save these values as GitHub repository secrets:" -ForegroundColor Yellow
Write-Host "  AZURE_TENANT_ID     = $TenantId"
Write-Host "  AZURE_CLIENT_ID     = $($app.AppId)"
Write-Host "  AZURE_CLIENT_SECRET = $($secret.SecretText)"
Write-Host "  SP_OBJECT_ID        = $($sp.Id)"
Write-Host ""
Write-Host "IMPORTANT: Copy the client secret now - it cannot be retrieved later." -ForegroundColor Red
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "  1. In the Fabric Admin Portal, add this SPN to the Fabric capacity as an Administrator."
Write-Host "  2. Enable 'Service principals can use Fabric APIs' in Fabric tenant settings."
Write-Host "  3. Add this SPN as a Member or Admin on each workspace (dev/test/prod)."
