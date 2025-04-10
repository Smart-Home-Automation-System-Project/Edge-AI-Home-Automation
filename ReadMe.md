# (Didn't test the documentation completely)

# IoT-Based-Smart-Home-Automation-System

## Edge AI Home Automation

### Project Setup Instructions

### Note
- train.csv - the training dataset for a week . (timestamp, day_of_week, hour, 3 lights , 3 thermostats)
- radar_sensors.csv - contains radar sensor data (which indicate whether a person is in a room or not)
- test.csv  - test data (contains data that needs to be send to predict.py every 15mins)(only 1 row/line of data)
- predictions.csv - predicted results received from predict.py 
- model.h5  - mode returned after running train.py

#### Prerequisites

Before setting up the project, make sure you have the following:

- [**Python 3.11.8**](https://www.python.org/downloads/release/python-3118/)   installed
- [**TensorFlow 2.16.1**](https://pypi.org/project/tensorflow/2.16.1/#files) installed
- [**How to  install Tensorflow(Youtube)**](https://youtu.be/0w-D6YaNxk8?feature=shared)


#### Installing Dependencies

Install the required dependencies for the project. You can use the following commands to install the necessary packages:

1. **Create a virtual environment**: 
   ```bash
   python -m venv venv
   ```

2. **Activate the virtual environment**:
   
   On Windows:
   ```bash
   venv\Scripts\activate
   ```
   
   On macOS/Linux: (didn't check)
   ```bash
   source venv/bin/activate
   ```
3. **Install the MQTT Python client(on both publisher and subscriber PCs)**:
   ```bash
   pip install paho-mqtt
   ```

4. **Install the MQTT Broker (on another laptop/ vbox running on the same PC)**:
   Linux (Ubuntu/Debian)
   ```bash
   sudo apt update
   sudo apt install -y mosquitto mosquitto-clients
   sudo systemctl enable mosquitto
   sudo systemctl start mosquitto
   sudo systemctl status mosquitto
   sudo systemctl stop mosquitto 
   ```   
   Windows
   Download the installer from the official Mosquitto site:
   https://mosquitto.org/download/

   Choose the Windows installer (.exe), run it, and follow the install instructions.
   Make sure to install the service when prompted.

   If you want to start Mosquitto manually later, you can do:
   ```bash
   "C:\Program Files\mosquitto\mosquitto.exe"
   ```
   Optional: Add C:\Program Files\mosquitto to your PATH for easier access via command line. 

#### Updating File Paths in .env

Make sure to replace any hardcoded file paths in the .env file with paths specific to your local environment.

- Paste the path to the project.

- Paste the IP address of the MQTT Broker

### Setup the Project (only need to do once)

**Setup DB**:   Inside database folder run db_setup.py, insert_data.py, export_train_csv.py and export_test_csv.py respectively.


### Running the Project
#### Need 3 machines
1. **Start MQTT Broker (on another laptop/ vbox running on the same PC)**:
   Start broker by using (linux)
   ```bash
   sudo systemctl start mosquitto
   ```
   Or run mosquitto.exe in Windows.
 
2. **Run mqtt_subscriber.py (on another laptop/ vbox running on the same PC)**

3. **Run random_test_write.py.py**
 
4. **Run weekly_check_loop.py**