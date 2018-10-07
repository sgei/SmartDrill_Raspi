# SmartDrill_Raspi

The setup will only work on a Raspbian Desktop version with user "pi".
The newer Raspian versions have a real-vnc-server pre-installed. You can activate it via raspi-config.
To get the VNC connection you need to download the [RealVNC Viewer](https://www.realvnc.com/de/connect/download/viewer/).

## Install SmartDrill on Raspberry Pi

### Clone project to /home/pi

- `cd /home/pi`
- `git clone https://github.com/sgei/SmartDrill_Raspi.git`

### Run install script

- `cd SmartDrill_Raspi`
- `chmod +x setup_smartdrill.sh`
- `./setup_smartdrill.sh`

### Insert Connection String in "smartdrill_azure.py"

Add connection string to smartdrill_azure.py line 44:

CONNECTION_STRING = 'HostName=**[NAME]**.azure-devices.net;DeviceId=**[ID]**;SharedAccessKey=**[KEY]**'

[NAME]
[ID]
[KEY]

---
## Information (all done by setup_smartdrill.sh)

### Needed packages

#### azure-iothub-device-client

`sudo pip install azure-iothub-device-client`

`sudo apt-get install libboost-python-dev`

[Azure IoT Hub Device Client SDK](https://pypi.org/project/azure-iothub-device-client/)

#### inotify

 `sudo pip install inotify`
 
### Prepare azure-iothub-device-client "smartdrill_azure.py"
 
Add connection string to smartdrill_azure.py line 449:

CONNECTION_STRING = 'HostName=**[NAME]**.azure-devices.net;DeviceId=**[ID]**;SharedAccessKey=**[KEY]**'

[NAME]
[ID]
[KEY]
