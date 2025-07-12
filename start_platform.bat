@echo off
echo ========================================
echo Starting Akio Unified Platform
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.7+ from https://python.org
    pause
    exit /b 1
)

REM Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Node.js is not installed or not in PATH
    echo Please install Node.js from https://nodejs.org
    pause
    exit /b 1
)

REM Install Python dependencies if needed
echo Checking Python dependencies...
pip install -r requirements_unified.txt

REM Check if CRM node_modules exists
if not exist "crm-integration-prototype\node_modules" (
    echo Installing CRM dependencies...
    cd crm-integration-prototype
    npm install
    cd ..
)

REM Start the unified platform
echo.
echo Starting Unified Platform Dashboard...
echo.
echo The dashboard will open in your browser at http://localhost:8501
echo.
echo Press Ctrl+C to stop all services
echo.
streamlit run unified_platform.py

pause