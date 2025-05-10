#!/bin/bash

# Set terminal text color to green
tput setaf 2

echo "==================================================="
echo " AI Home Automation System - MQTT BROKER"
echo " Version: 1.0.0 (Stable)"
echo " Status: Running..."
echo "==================================================="

# Start Mosquitto with config file and verbose mode
mosquitto -c "./config/mosquitto.conf" -v

# Reset terminal color
tput sgr0

# Pause until user presses enter
read -p "Press ENTER to exit..."
