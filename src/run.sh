#!/bin/bash

# Set terminal text color to green
tput setaf 2

echo "=============================================="
echo " AI Home Automation System - FULL STARTUP"
echo "=============================================="

# Step 1: Start MQTT broker
echo "[1/4] Starting MQTT Broker..."
./start-mqtt.sh &
sleep 3  # Delay to allow MQTT to fully initialize

# Step 2: Start Core System
echo "[2/4] Starting Core System..."
python3 core.py &
sleep 2

# Step 3: Start Web Interface
echo "[3/4] Starting Web Interface..."
python3 web_interface.py &
sleep 2

# Step 4: Start AI Module
echo "[4/4] Starting AI Engine..."
python3 ai_main.py &

# Reset terminal color
tput sgr0

echo "All components launched."
