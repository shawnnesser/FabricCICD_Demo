# =============================================================================
# Setup script - creates the Python venv on C:\ drive (not OneDrive)
# to avoid certificate/permission issues with OneDrive sync.
# Run this once before starting development.
# =============================================================================

$VenvPath = "C:\venvs\fabric-cicd-demo"
$ReqFile  = Join-Path $PSScriptRoot "..\requirements.txt"

Write-Host "Creating virtual environment at: $VenvPath" -ForegroundColor Cyan

# Create directory if it doesn't exist
if (-not (Test-Path $VenvPath)) {
    New-Item -ItemType Directory -Path $VenvPath -Force | Out-Null
}

# Create the venv
python -m venv $VenvPath

# Activate and install dependencies
$ActivateScript = Join-Path $VenvPath "Scripts\Activate.ps1"
& $ActivateScript

pip install --upgrade pip
pip install -r $ReqFile

Write-Host ""
Write-Host "Setup complete." -ForegroundColor Green
Write-Host "To activate the venv in future sessions run:" -ForegroundColor Yellow
Write-Host "  & 'C:\venvs\fabric-cicd-demo\Scripts\Activate.ps1'" -ForegroundColor Yellow
