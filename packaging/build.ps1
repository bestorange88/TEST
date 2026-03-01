# PowerShell build script for RecoveryTron
# Usage: .\packaging\build.ps1

$ErrorActionPreference = "Stop"

Write-Host "=== RecoveryTron Build Script ===" -ForegroundColor Cyan

# Check Python version
$pythonVersion = python --version 2>&1
Write-Host "Python: $pythonVersion"

# Install dependencies
Write-Host "`nInstalling dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt

# Run tests
Write-Host "`nRunning tests..." -ForegroundColor Yellow
python -m pytest tests/ -v
if ($LASTEXITCODE -ne 0) {
    Write-Host "Tests failed! Aborting build." -ForegroundColor Red
    exit 1
}

# Build with PyInstaller
Write-Host "`nBuilding executable..." -ForegroundColor Yellow
pyinstaller packaging/recovery_tron.spec --distpath dist --workpath build --clean -y

if (Test-Path "dist/RecoveryTron.exe") {
    $size = (Get-Item "dist/RecoveryTron.exe").Length / 1MB
    Write-Host "`nBuild successful!" -ForegroundColor Green
    Write-Host "Output: dist/RecoveryTron.exe ($([math]::Round($size, 2)) MB)"
} else {
    Write-Host "`nBuild failed - executable not found." -ForegroundColor Red
    exit 1
}
