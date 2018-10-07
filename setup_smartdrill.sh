#!/bin/bash

SPATH="/home/pi/intershop/scripts"

clear

echo -e "\n### Copy "intershop"-folder to /home/pi..."
cp -r ./home/pi/intershop /home/pi
echo -e "Done..."

echo -e "\n### Set file execution rights..."
chmod +x $SPATH/*.sh
chmod +x $SPATH/drill/autostart.sh
chmod +x $SPATH/drill/drill.py
chmod +x $SPATH/drill/reset.sh
chmod +x $SPATH/drill/smartdrill_azure.py
chmod +x $SPATH/shutdown/shutdown.py
echo -e "Done..."

echo -e "\n### Install service for shutdown script..."
sudo cp $SPATH/shutdown/shutdown.service /lib/systemd/system
sudo systemctl enable shutdown.service
sudo systemctl start shutdown.service
echo -e "Done..."

echo -e "\n### Checking for azure-iothub-device-client..."
azure=""
azure=`sudo pip freeze | grep -a -e "azure-iothub-device-client"`

if [ -z "$azure" ]; then
	echo "-> not installed"
	echo "-> install package..."
	sudo pip install --exists-action a azure-iothub-device-client
else
	echo "-> package already installed"
fi
echo -e "Done..."

echo -e "\n### Checking for libboost-python-dev..."
libboost=""
libboost=`sudo dpkg -l | grep -a -e "libboost-python-dev"`

if [ -z "$libboost" ]; then
	echo "-> not installed"
	echo "-> install package..."
	sudo apt-get -qy install libboost-python-dev
else
	echo "-> package already installed"
fi
echo -e "Done..."

echo -e "\n### Checking for inotify..."
inotify=""
inotify=`sudo pip freeze | grep -a -e "inotify" | grep -a -v "pyinotify"`

if [ -z "$inotify" ]; then
	echo "-> not installed"
	echo "-> install package..."
	sudo pip install --exists-action a inotify
else
	echo "-> package already installed"
fi
echo -e "Done..."

echo -e "\n### Install autostart script..."
autostart=""
autostart=`cat /home/pi/.config/lxsession/LXDE-pi/autostart | grep -a -e "autostart.sh"`

if [ -z "$autostart" ]; then
	echo "-> autostart not configured"
	echo "-> configure autostart..."
	echo -e "\n\n# Intershop SmartDrill for Raspi" >> /home/pi/.config/lxsession/LXDE-pi/autostart
	echo "@/home/pi/intershop/scripts/drill/autostart.sh" >> /home/pi/.config/lxsession/LXDE-pi/autostart
else
	echo "-> autostart already configures"
fi
echo -e "Done..."

echo -e "\n"

exit 0