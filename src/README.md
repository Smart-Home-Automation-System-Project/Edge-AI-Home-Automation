
# Edge AI Home Automation

A smart home system with customizable controls for lights, switches, temperature, and doors, featuring secure login, automatic database backup and error detection, and LSTM-based predictions every 10 minutes. Supports integrations with surveillance, voice-gesture control, and energy optimization systems for enhanced automation


## Features

- Predictive Analytics: Implements an LSTM-based model for accurate predictions every 10 minutes, optimizing system efficiency.
- Intuitive User Interface: Provides seamless control over lights, switches, temperature, and doors, ensuring ease of use.
- Customizable Modules: Allows personalized home automation configurations for tailored user experiences.
- Secure Authentication: Enforces password-protected login to safeguard user access.
- Database Management: Ensures automatic backups and error detection to maintain data integrity.
- Smart System Integrations: Supports:
    - [Secure Access Surveillance System](https://github.com/Smart-Home-Automation-System-Project/Secure-Access-Surveillance-System) for enhanced security monitoring.
    - [Voice Gesture Based Control System](https://github.com/Smart-Home-Automation-System-Project/Voice-Gesture-Based-Control) for hands-free smart home interaction.
    - [Energy Consumption Optimization System](https://github.com/Smart-Home-Automation-System-Project/Energy-Consumption-Optimization) for efficient energy management.

## Screenshots

![Image](https://github.com/user-attachments/assets/2f260f7b-665e-4055-9c04-79cc2c0d06ab)
![Image](https://github.com/user-attachments/assets/20e881aa-7fc8-4f50-be0d-15bafb0ea184)
![Image](https://github.com/user-attachments/assets/0d8feff6-4bc4-4a7e-9f80-e3ae5d600192)
![Image](https://github.com/user-attachments/assets/02cefbfd-7407-4c85-a9b7-de968ab112f8)
## Installation

- Run the following command to clone the required repositories:
    ```bash
    git clone https://github.com/Smart-Home-Automation-System-Project/Edge-AI-Home-Automation
    ```
For Ubuntu:
- Install Mosquitto and client tools:
    ```bash
    sudo apt install -y mosquitto mosquitto-clients
    ```
- Enable and start the Mosquitto service:
    ```bash
    sudo systemctl enable mosquitto
    sudo systemctl start mosquitto
    ```
- Navigate to `src`:
    ```bash
    cd Edge-AI-Home-Automation/src/
    ```
- Generate a password file for your system. Default username and password are `admin` and `1234`. You can generate a new password file:
    ```bash
    sudo mosquitto_passwd -c /config/passwordfile.txt [your_username]
    ```
    Then enter a secure password when prompted.
- Install dependencies
    ```bash
    pip install -r requirements.txt
    ```
- Start system
    - Make executable:
        ```bash
        chmod +x start-system.sh
        chmod +x backup-db.sh
        chmod +x start-mqtt.sh
        ```
    - Modify 'config/.env' and update IPs, `JWT_SECRET_KEY`,  username and passwords:
        ```bash
        MQTT_USERNAME=admin
        MQTT_PASSWORD=1234
        MQTT_PORT=1883
        JWT_SECRET_KEY=MTI3LjAuMC4xIC0gLSBbMjAvQXByLzIwMjUgMTA6NTU6MDFdICJHRVQgL2F
        UI_PASSWORD=abcd
        IP_SAS_SYSTEM=[IP OF Secure-Access-Surveillance-System]
        IP_ECO_SYSTEM=[IP OF Energy-Consumption-Optimization]
        ```
    - Run it:
        ```bash
        ./start-system.sh
        ```
- Setup auto-start
    - Create a systemd service
        ```bash
        sudo nano /etc/systemd/system/ai-home.service
        ```
    - Paste the following:
        ```bash
        [Unit]
        Description=AI Home Automation Startup Script
        After=network.target

        [Service]
        ExecStart=/bin/bash [/path/to/start-system.sh]
        WorkingDirectory=[/path/to/]
        Restart=always
        User=[your_username]

        [Install]
        WantedBy=multi-user.target
        ```

## Authors

- [@Sahan Gunasekara](https://github.com/sahan974)
- [@Malaka Gunawardana](https://github.com/sdmdg)
- [@Himala Gunathilaka](https://github.com/HimalaGunathilaka)
- [@Isurika Gunasekara](https://github.com/isurika23)
- [@Nesandu Sithnuka](https://github.com/NesanduGMS)
