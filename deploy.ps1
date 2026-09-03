Write-Host "========================================="
Write-Host "  KSP Sentinel - Backend Deploy Script"
Write-Host "========================================="
Write-Host "Step 1: Vendoring dependencies into backend/vendor..."

# Remove old vendor folder if it exists
if (Test-Path "backend/vendor") {
    Remove-Item -Recurse -Force "backend/vendor"
}

# Install dependencies into vendor directory (Targeting Linux for AppSail)
pip install -r backend/requirements.txt -t backend/vendor --no-cache-dir --platform manylinux2014_x86_64 --only-binary=:all:

Write-Host "========================================="
Write-Host "Step 2: Deploying to Catalyst AppSail..."
catalyst deploy --only appsail --non-interactive

Write-Host "========================================="
Write-Host "Deploy Complete! The server will now start instantly."
