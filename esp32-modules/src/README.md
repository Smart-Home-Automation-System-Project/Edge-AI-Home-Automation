
# Edge AI Home Automation Sensor Modules

Edge AI Home Automation Sensor Modules are intelligent, distributed components designed to monitor and control various aspects of a smart home environment.

## Features

- Energy Tracking: Monitor power usage at appliance.
- MQTT Communication: Seamlessly integrate with the core system using lightweight, real-time MQTT messaging.
- Simple and User-Friendly Interface: Streamlined Web UI for seamless system configuration and management.
- Local Data Storage: Ensures functionality during network failures, with automatic data transmission once connectivity is restored.

## Screenshots

![Image](https://github.com/user-attachments/assets/23ae7bcb-85fe-4dc1-9907-e5c823823971)
![Image](https://github.com/user-attachments/assets/0d8feff6-4bc4-4a7e-9f80-e3ae5d600192)

## 🔌 Sensor Module Installation (ESP32)

Follow these steps to set up a sensor module for the Edge AI Home Automation System using an ESP32 board:

1. Flash MicroPython on the ESP32

    - Install MicroPython firmware on your ESP32.
    - Refer to the official [MicroPython tutorial for ESP32](https://docs.micropython.org/en/latest/esp32/tutorial/intro.html) for detailed instructions.

2. Upload Required Files

- Copy the following files to the ESP32’s local storage using a tool like Thonny or ampy:
    - `boot.py`
    - `main.py`
    - `webserver.py`

3. Configure the Device

- You can generate a unique `client_id` and update `main.py` using any text editor
- Connect the sensor pins according to the provided wiring diagram.

    ![Image](https://github.com/user-attachments/assets/3f8aff05-b99f-4193-9053-7bc39d4eaacc)

4. Connect to Configuration Interface

- Restart the module. It will create a Wi-Fi access point named: `SensorModule`.
- Connect your computer or phone to this access point.
- Open a browser and navigate to http://192.168.4.1.

    ![Image](https://github.com/user-attachments/assets/23ae7bcb-85fe-4dc1-9907-e5c823823971)

5. Join Home Network

- On the configuration page, enter your home Wi-Fi credentials.
- Once connected, the sensor will automatically appear in the “Add Sensor” page of the [Edge-AI-Home-Automation](https://github.com/Smart-Home-Automation-System-Project/Edge-AI-Home-Automation) will show your new sensor with it's `client_id`.

6. Final Setup

- Select the newly detected sensor using its `client id`.
- Assign a friendly name and add it to your system.

## Authors

- [@Malaka Gunawardana](https://github.com/sdmdg)
