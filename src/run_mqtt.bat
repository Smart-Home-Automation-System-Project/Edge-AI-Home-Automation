@echo off

color A

echo ===================================================
echo AI Home Automation System - MQTT BROKER
echo Version: 1.0.0 (Stable)
echo Status: Running...
echo ===================================================

mosquitto -c ".\config\mosquitto.conf" -v

pause