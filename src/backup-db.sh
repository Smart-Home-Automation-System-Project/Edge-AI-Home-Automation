#!/bin/bash

# Set terminal text color to green
tput setaf 2

echo "==================================================="
echo " AI Home Automation System - DB Auto Backup"
echo " Version: 1.0.0 (Stable)"
echo " Status: Running..."
echo "==================================================="

# Navigate to the database directory
cd "$(dirname "$0")/database"

# Run the Python backup script
python3 backup_restore_script.py backup \
    --cred-path ../config/firebase_credentials.json \
    --db-path database.db \
    --days 1

# Reset terminal color
tput sgr0

# Pause until the user presses ENTER
read -p "Press ENTER to exit..."
