# Edge AI Home Automation

## How to run the code inside docker container

#### Prerequisites
- **Docker (around 500 MB to 1 GB)**: Make sure Docker is installed on your machine. You can download Docker from the official website.
 
- **Docker Compose (10-30 MB)**: Docker Compose is required to manage multi-container Docker applications. You can find installation instructions here.
- **Set MQTT Broker IP address inside docker-compose.yml**: Paste the mqtt broker ip address inside docker-compose.yml-> services-> environment

### 1) Build the Docker image:
Run the following command to build the Docker image based on the Dockerfile.
#### **NOTE : Building image for the 1st time will consume a significant amount of data and time** 
(to download the necessary base images and dependencies. Ubuntu base image itself is around 50 MB to 200 MB).
Subsequent builds will use cached layers, so data usage will be much lower and faster building , unless there are changes to the dependencies.
```bash
   docker-compose build
```
### 2) Start the container:
Run the following command to start the Docker container in detached mode.This will start the container and run it in the background.

```bash
   docker-compose up -d
```
### 3) Check the running containers (Optional):
To verify that your container is running, use the following command:

```bash
   docker ps
```
### 4) Get a terminal to run files/commands
This gives you a terminal session inside the container where you can run commands
Using this terminal you can run pythin files and navigate through folders .
You can run the following commands in multiple CLI's to get multiple terminals at the same time.  
```bash
   docker exec -it project-home-automation-1 bash
```
**NOTE: By default docker runs 'lights_temp_automation/weekly_check_loop.py' file.But you can stop it by pressing Ctr+C and run any file using terminal that we created above .**

### 5) Stop the container when finished:
To exit the terminal session inside the Docker container
```bash
   exit
```
Then, stop the container when you're done, by running the following command:

```bash
   docker-compose down
```
