@echo off

color A

echo ===================================================
echo AI Home Automation System - DB Auto Backup
echo Version: 1.0.0 (Stable)
echo Status: Running...
echo ===================================================

cd database
python backup_restore_script.py backup --cred-path ../config/firebase_credentials.json --db-path database.db --days 1

pause