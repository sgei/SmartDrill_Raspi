# SmartDrill_Raspi

## Needed packages

### azure-iothub-device-client

`sudo pip install azure-iothub-device-client`

`sudo apt-get install libboost-python-dev`

[Azure IoT Hub Device Client SDK](https://pypi.org/project/azure-iothub-device-client/)

### inotify

 `sudo pip install inotify`
 
 ## Prepare azure-iothub-device-client "smartdrill_azure.py"
 
Add connection string to smartdrill_azure.py line 449:

CONNECTION_STRING = 'HostName=**[NAME]**.azure-devices.net;DeviceId=**[ID]**;SharedAccessKey=**[KEY]**'

[NAME]
[ID]
[KEY]
