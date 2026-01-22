@echo off
echo ================================
echo MongoDB + Python Setup Script
echo ================================
echo.

echo Step 1: Installing Python packages...
pip install -r requirements.txt

echo.
echo Step 2: Verifying MongoDB connection...
python -c "from app import get_mongo_db; db = get_mongo_db(); print('✅ MongoDB connected!' if db else '❌ MongoDB not available')"

echo.
echo Step 3: Setup complete!
echo.
echo Next steps:
echo - Make sure MongoDB is running (mongod.exe or service)
echo - Run: python app.py
echo - Visit: http://localhost:5000
echo.
echo For more details, see MONGODB_SETUP.md
echo.
pause
