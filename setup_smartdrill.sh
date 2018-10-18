#!/bin/bash

HOME="/home/pi"
IPATH="$HOME/intershop"
SPATH="$HOME/intershop/scripts"
DPATH="$HOME/intershop/scripts/drill"
VAR=""

clear

sudo apt-get autoremove
sudo apt-get autoclean
sudo apt-get clean
sudo apt-get update
sudo apt-get -y upgrade

clear

echo -e "\n### Copy "intershop"-folder to $HOME..."
cp -r .$HOME/intershop $HOME
echo -e "Done..."

echo -e "\n### Set file execution rights..."
chmod +x $SPATH/*.sh
chmod +x $DPATH/autostart.sh
chmod +x $DPATH/drill.py
chmod +x $DPATH/reset.sh
chmod +x $DPATH/smartdrill_azure.py
chmod +x $SPATH/shutdown/shutdown.py
echo -e "Done..."

echo -e "\n### Install service for shutdown script..."
sudo cp $SPATH/shutdown/shutdown.service /lib/systemd/system
sudo systemctl enable shutdown.service
sudo systemctl start shutdown.service
echo -e "Done..."

read -p "press <ENTER> to continue"

echo -e "\n### Checking for azure-iothub-device-client..."
VAR=""
VAR=`sudo pip freeze | grep -a -e "azure-iothub-device-client"`

if [ -z "$VAR" ]; then
	echo "-> not installed"
	echo "-> install package..."
	sudo pip install --exists-action a azure-iothub-device-client
else
	echo "-> package already installed"
fi
echo -e "Done..."

read -p "press <ENTER> to continue"

echo -e "\n### Checking for libboost-python-dev..."
VAR=""
VAR=`sudo dpkg -l | grep -a -e "libboost-python-dev"`

if [ -z "$VAR" ]; then
	echo "-> not installed"
	echo "-> install package..."
	sudo apt-get -qy install libboost-python-dev
else
	echo "-> package already installed"
fi
echo -e "Done..."

read -p "press <ENTER> to continue"

echo -e "\n### Checking for inotify..."
VAR=""
VAR=`sudo pip freeze | grep -a -e "inotify" | grep -a -v "pyinotify"`

if [ -z "$VAR" ]; then
	echo "-> not installed"
	echo "-> install package..."
	sudo pip install --exists-action a inotify
else
	echo "-> package already installed"
fi
echo -e "Done..."

read -p "press <ENTER> to continue"

echo -e "\n### Install autostart script..."
VAR=""
VAR=`cat $HOME/.config/lxsession/LXDE-pi/autostart | grep -a -e "autostart.sh"`

if [ -z "$VAR" ]; then
	echo "-> autostart not configured"
	echo "-> configure autostart..."
	echo -e "\n\n# Intershop SmartDrill for Raspi" >> $HOME/.config/lxsession/LXDE-pi/autostart
	echo "@$HOME/intershop/scripts/drill/autostart.sh" >> $HOME/.config/lxsession/LXDE-pi/autostart
else
	echo "-> autostart already configures"
fi
echo -e "Done..."

echo -e "\n"

exit 0