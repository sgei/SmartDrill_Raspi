#!/bin/bash

IPATH="/home/pi/intershop"
SPATH="/home/pi/intershop/scripts"
DPATH="/home/pi/intershop/scripts/drill"
MODULE=""

clear

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

read -p "press <ENTER> to continue"

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

read -p "press <ENTER> to continue"

echo -e "\n### Checking for package.json file"
MODULE=""
MODULE=`ls -l $DPATH | grep -ae "package.json"`

if [ -z "$MODULE" ]; then
	echo "-> file does not exist"
	echo "-> create file..."
	cp package.json $DPATH
else
	echo "-> file exist"
fi
echo -e "Done..."

echo -e "\n### Checking for web3"
MODULE=""
cd $DPATH
MODULE=`npm list --depth=0 | grep -ae "web3"`

if [ -z "$MODULE" ]; then
	echo "-> not installed"
	echo "-> install package..."
	npm install web3
else
	echo "-> package already installed"
fi
echo -e "Done..."

read -p "press <ENTER> to continue"

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

read -p "press <ENTER> to continue"

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

read -p "press <ENTER> to continue"

echo -e "\n### Checking for ganache-cli"
MODULE=""
cd $DPATH
MODULE=`npm list --depth=0 | grep -ae "ganache-cli"`

if [ -z "$MODULE" ]; then
	echo "-> not installed"
	echo "-> install package..."
	npm install ganache-cli
else
	echo "-> package already installed"
fi
echo -e "Done..."

read -p "press <ENTER> to continue"

echo -e "\n### Checking for config.json"
MODULE=""
MODULE=`ls -l $DPATH | grep -ae "config.json"`

if [ -z "$MODULE" ]; then
	echo "-> file does not exist"
	echo "-> create file..."
	cp config.json $DPATH
else
	echo "-> file exist"
fi
echo -e "Done..."

echo -e "\n### Checking for index.js"
MODULE=""
MODULE=`ls -l $DPATH | grep -ae "index.js"`

if [ -z "$MODULE" ]; then
	echo "-> file does not exist"
	echo "-> create file..."
	cp index.js $DPATH
else
	echo "-> file exist"
fi
echo -e "Done..."

echo -e "\n"

exit 0