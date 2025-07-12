@echo off
echo ========================================
echo Starting All Akio Services
echo ========================================
echo.

REM Start from the Akio-stage directory
cd /d C:\Users\Rizvi\Akio-stage

echo [1/5] Starting Email Assistant...
start "Email Assistant" cmd /k "cd /d C:\Users\Rizvi\Akio-stage\Email-Assistant && python -m streamlit run email_assistant.py"
timeout /t 3 >nul

echo [2/5] Starting Call Metrics API...
start "Call Metrics API" cmd /k "cd /d C:\Users\Rizvi\Akio-stage\Call-System && python main.py"
timeout /t 3 >nul

echo [3/5] Starting Call Metrics Dashboard...
start "Call Dashboard" cmd /k "cd /d C:\Users\Rizvi\Akio-stage\Call-System && python -m streamlit run dashboard.py --server.port 8502"
timeout /t 3 >nul

echo [4/5] Starting CRM Integration...
start "CRM Integration" cmd /k "cd /d C:\Users\Rizvi\Akio-stage\crm-integration-prototype && npm start"
timeout /t 3 >nul

echo [5/5] Starting Unified Portal...
start "Unified Portal" cmd /k "cd /d C:\Users\Rizvi\Akio-stage && python -m streamlit run unified_services_portal.py --server.port 8505"

echo.
echo ========================================
echo All services are starting!
echo ========================================
echo.
echo Services will open in separate windows.
echo.
echo URLs:
echo - Unified Portal:      http://localhost:8505
echo - Email Assistant:     http://localhost:8501
echo - Call Metrics API:    http://localhost:8000
echo - Call Dashboard:      http://localhost:8502
echo - CRM Integration:     http://localhost:3000
echo.
echo To stop all services, close each window.
echo.
pause