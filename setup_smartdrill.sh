#!/bin/bash

IPATH="/home/pi/intershop"
SPATH="/home/pi/intershop/scripts"
MODULE=""

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
MODULE=""
MODULE=`sudo pip freeze | grep -a -e "azure-iothub-device-client"`

if [ -z "$MODULE" ]; then
	echo "-> not installed"
	echo "-> install package..."
	sudo pip install --exists-action a azure-iothub-device-client
else
	echo "-> package already installed"
fi
echo -e "Done..."

echo -e "\n### Checking for libboost-python-dev..."
MODULE=""
MODULE=`sudo dpkg -l | grep -a -e "libboost-python-dev"`

if [ -z "$MODULE" ]; then
	echo "-> not installed"
	echo "-> install package..."
	sudo apt-get -qy install libboost-python-dev
else
	echo "-> package already installed"
fi
echo -e "Done..."

echo -e "\n### Checking for inotify..."
MODULE=""
MODULE=`sudo pip freeze | grep -a -e "inotify" | grep -a -v "pyinotify"`

if [ -z "$MODULE" ]; then
	echo "-> not installed"
	echo "-> install package..."
	sudo pip install --exists-action a inotify
else
	echo "-> package already installed"
fi
echo -e "Done..."

echo -e "\n### Install autostart script..."
MODULE=""
MODULE=`cat /home/pi/.config/lxsession/LXDE-pi/autostart | grep -a -e "autostart.sh"`

if [ -z "$MODULE" ]; then
	echo "-> autostart not configured"
	echo "-> configure autostart..."
	echo -e "\n\n# Intershop SmartDrill for Raspi" >> /home/pi/.config/lxsession/LXDE-pi/autostart
	echo "@/home/pi/intershop/scripts/drill/autostart.sh" >> /home/pi/.config/lxsession/LXDE-pi/autostart
else
	echo "-> autostart already configures"
fi
echo -e "Done..."

echo -e "\n### Checking for nodejs"
MODULE=""
MODULE=`sudo dpkg -l | grep -a -e "nodejs"`

if [ -z "$MODULE" ]; then
	echo "-> not installed"
	echo "-> install package..."
	sudo apt-get -qy install nodejs
else
	echo "-> package already installed"
fi
echo -e "Done..."

echo -e "\n### Checking for npm"
MODULE=""
MODULE=`sudo dpkg -l | grep -a -e "npm"`

if [ -z "$MODULE" ]; then
	echo "-> not installed"
	echo "-> install package..."
	sudo apt-get -qy install npm
else
	echo "-> package already installed"
fi
echo -e "Done..."

echo -e "\n### Checking for web3"
MODULE=""
MODULE=`sudo npm list --depth=0 | grep -a -e "web3"`

if [ -z "$MODULE" ]; then
	echo "-> not installed"
	echo "-> install package..."
	cd SPATH/drill
	npm install -g web3
else
	echo "-> package already installed"
fi
echo -e "Done..."

echo -e "\n### Checking for golang"
MODULE=""
MODULE=`sudo dpkg -l | grep -a -e "golang"`

if [ -z "$MODULE" ]; then
	echo "-> not installed"
	echo "-> install package..."
	sudo apt-get -yq install golang
else
	echo "-> package already installed"
fi
echo -e "Done..."

echo -e "\n### Checking for geth"
MODULE=""
MODULE=`sudo ls -l /usr/local/bin | grep -ae "geth"`
ARM7=`cat /proc/cpuinfo | grep -ae "ARMv7"`
ARM6=`cat /proc/cpuinfo | grep -ae "ARMv6"`

if [ -z "$MODULE" ]; then
	echo "-> not installed"
	echo "-> install package..."
	cd $IPATH
	if [ -n "ARM7" ]; then
		wget https://gethstore.blob.core.windows.net/builds/geth-linux-arm7-1.8.17-8bbe7207.tar.gz
		tar -xvzf geth-linux-arm7-1.8.17-8bbe7207.tar.gz
		sudo mv geth-linux-arm7-1.8.17-8bbe7207/geth /usr/local/bin
		sudo chown root:staff /usr/local/bin/geth
		rm -rf geth-linux-arm7-1.8.17-8bbe7207*
	fi
	if [ -n "ARM6" ]; then
		wget https://gethstore.blob.core.windows.net/builds/geth-linux-arm6-1.8.17-8bbe7207.tar.gz
		tar -xvzf geth-linux-arm6-1.8.17-8bbe7207.tar.gz
		sudo mv geth-linux-arm6-1.8.17-8bbe7207/geth /usr/local/bin
		sudo chown root:staff /usr/local/bin/geth
		rm -rf geth-linux-arm6-1.8.17-8bbe7207*
	fi
else
	echo "-> package already installed"
fi
echo -e "Done..."

echo -e "\n### Checking for ganache-cli"
MODULE=""
MODULE=`sudo npm list --depth=0 | grep -a -e "ganache-cli"`

if [ -z "$MODULE" ]; then
	echo "-> not installed"
	echo "-> install package..."
	cd $SPATH/drill
	npm install -g ganache-cli
else
	echo "-> package already installed"
fi
echo -e "Done..."

echo -e "\n"

exit 0