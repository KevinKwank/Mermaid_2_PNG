# Mermaid to PNG Converter - Installation Script
# This script installs all required dependencies

Write-Host "🚀 Installing Mermaid to PNG Converter..." -ForegroundColor Green

# Check if Node.js is installed
Write-Host "📦 Checking Node.js installation..." -ForegroundColor Yellow
try {
    $nodeVersion = node --version
    Write-Host "✅ Node.js is installed: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Node.js is not installed!" -ForegroundColor Red
    Write-Host "Please install Node.js from https://nodejs.org/" -ForegroundColor Yellow
    exit 1
}

# Check if Python is installed
Write-Host "🐍 Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version
    Write-Host "✅ Python is installed: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python is not installed!" -ForegroundColor Red
    Write-Host "Please install Python from https://python.org/" -ForegroundColor Yellow
    exit 1
}

# Install Node.js dependencies
Write-Host "📦 Installing Mermaid CLI..." -ForegroundColor Yellow
npm install

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Mermaid CLI installed successfully" -ForegroundColor Green
} else {
    Write-Host "❌ Failed to install Mermaid CLI" -ForegroundColor Red
    exit 1
}

# Test the installation
Write-Host "🧪 Testing installation..." -ForegroundColor Yellow
python mermaid_to_png.py --check

if ($LASTEXITCODE -eq 0) {
    Write-Host "🎉 Installation completed successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Usage examples:" -ForegroundColor Cyan
    Write-Host "  python mermaid_to_png.py --sample" -ForegroundColor White
    Write-Host "  python mermaid_to_png.py -f sample.mmd" -ForegroundColor White
    Write-Host "  python mermaid_to_png.py --text 'graph TD; A-->B'" -ForegroundColor White
} else {
    Write-Host "❌ Installation test failed" -ForegroundColor Red
    exit 1
}
