@echo off
color A

echo ==================================================
echo     AI Home Automation System - FULL STARTUP
echo ==================================================

echo [1/4] Starting MQTT Broker...
start "" /B start-mqtt.bat
timeout /t 3 >nul

echo [2/4] Starting Core System...
start "" /B python core.py
timeout /t 2 >nul

echo [3/4] Starting Web Interface...
start "" python web_interface.py
timeout /t 2 >nul

echo [4/4] Starting AI Engine...
start "" python ai_main.py

echo.
echo All components launched.
