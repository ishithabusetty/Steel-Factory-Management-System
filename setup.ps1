# Steel Factory Management System - MongoDB Setup Script
# Run: powershell -ExecutionPolicy Bypass -File setup.ps1

Write-Host "================================" -ForegroundColor Cyan
Write-Host "MongoDB + Python Setup Script" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Install dependencies
Write-Host "Step 1: Installing Python packages..." -ForegroundColor Yellow
pip install -r requirements.txt
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Packages installed successfully" -ForegroundColor Green
} else {
    Write-Host "❌ Package installation failed" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Step 2: Verify MongoDB
Write-Host "Step 2: Verifying MongoDB connection..." -ForegroundColor Yellow
$mongoTest = python -c "from app import get_mongo_db; db = get_mongo_db(); print('1' if db else '0')"
if ($mongoTest -eq "1") {
    Write-Host "✅ MongoDB connected successfully" -ForegroundColor Green
} else {
    Write-Host "⚠️  MongoDB not available (will work without it)" -ForegroundColor Yellow
    Write-Host "    To enable: Install MongoDB or configure MongoDB Atlas" -ForegroundColor Gray
}

Write-Host ""
Write-Host "================================" -ForegroundColor Cyan
Write-Host "Setup Complete!" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Start MongoDB (if using local): mongod" -ForegroundColor Gray
Write-Host "2. Run app: python app.py" -ForegroundColor Gray
Write-Host "3. Visit: http://localhost:5000" -ForegroundColor Gray
Write-Host ""
Write-Host "For detailed setup, see MONGODB_SETUP.md" -ForegroundColor Cyan
