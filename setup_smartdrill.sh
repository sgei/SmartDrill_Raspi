#!/bin/bash

HOME="/home/pi"
SETUP_PATH=`pwd`
IPATH="$HOME/intershop"
SPATH="$HOME/intershop/scripts"
DPATH="$HOME/intershop/scripts/drill"
VAR=""

f_clear() {
	clear

	sudo apt-get autoremove
	sudo apt-get autoclean
	sudo apt-get clean
	sudo apt-get update
	sudo apt-get -y upgrade

	clear
}

f_files() {
	echo -e "\n### Copy "intershop"-folder to $HOME..."
	read -p "press <ENTER> to continue"
	cp -r .$HOME/intershop $HOME
	echo -e "Done..."

	echo -e "\n### Set file execution rights..."
	read -p "press <ENTER> to continue"
	chmod +x $SPATH/*.sh
	chmod +x $DPATH/autostart.sh
	chmod +x $DPATH/drill.py
	chmod +x $DPATH/payment.py
	chmod +x $DPATH/reset.sh
	chmod +x $DPATH/smartdrill_azure.py
	chmod +x $SPATH/shutdown/shutdown.py
	echo -e "Done..."
}

f_shutdown() {
	echo -e "\n### Install service for shutdown script..."
	read -p "press <ENTER> to continue"
	sudo cp $SPATH/shutdown/shutdown.service /lib/systemd/system
	sudo systemctl enable shutdown.service
	sudo systemctl start shutdown.service
	echo -e "Done..."
}

f_azure() {
	echo -e "\n### Checking for azure-iothub-device-client..."
	read -p "press <ENTER> to continue"
	VAR=""
	ARM7=`cat /proc/cpuinfo | grep -ae "ARMv7"`
	ARM6=`cat /proc/cpuinfo | grep -ae "ARMv6"`

	if [ -n "$ARM7" ]; then
		echo "-> ARM7"
		VAR=`sudo pip freeze | grep -a -e "azure-iothub-device-client"`

		if [ -z "$VAR" ]; then
			echo "-> not installed"
			echo "-> install package..."
			sudo pip install --exists-action a azure-iothub-device-client
		else
			echo "-> package already installed"
		fi
	fi
	if [ -n "$ARM6" ]; then
		echo "-> ARM6"
		VAR=`ls -l $DPATH | grep -ae "iothub_client.so"`

		if [ -z "$VAR" ]; then
			echo "-> file does not exist"
			echo "-> copy file..."
			cp $SETUP_PATH/azure/iothub_client.so $DPATH
		else
			echo "-> file exist"
		fi
	fi
	echo -e "Done..."
}

f_libboost() {
	echo -e "\n### Checking for libboost-python-dev..."
	read -p "press <ENTER> to continue"
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
}

f_inotify() {
	echo -e "\n### Checking for inotify..."
	read -p "press <ENTER> to continue"
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
}

f_autostart() {
	echo -e "\n### Install autostart script..."
	read -p "press <ENTER> to continue"
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
}

f_clear
f_files
f_shutdown
f_azure
f_libboost
f_inotify
f_autostart

echo -e "\n"

exit 0