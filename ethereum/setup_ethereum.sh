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

f_nodejs() {
	echo -e "\n### Checking for nodejs"
	VAR=""
	VAR=`sudo dpkg -l | grep -a -e "nodejs"`

	if [ -z "$VAR" ]; then
		echo "-> not installed"
		echo "-> install package..."
		sudo apt-get -qy install nodejs
	else
		echo "-> package already installed"
	fi
	echo -e "Done..."
}

f_npm() {
	echo -e "\n### Checking for npm"
	VAR=""
	VAR=`sudo dpkg -l | grep -a -e "npm"`

	if [ -z "$VAR" ]; then
		echo "-> not installed"
		echo "-> install package..."
		sudo apt-get -qy install npm
	else
		echo "-> package already installed"
	fi
	echo -e "Done..."
}

f_files() {
	echo -e "\n### Checking for package.json file"
	VAR=""
	VAR=`ls -l $DPATH | grep -ae "package.json"`

	if [ -z "$VAR" ]; then
		echo "-> file does not exist"
		echo "-> create file..."
		cp $SETUP_PATH/package.json $DPATH
	else
		echo "-> file exist"
	fi
	echo -e "Done..."

	echo -e "\n### Checking for README.md file"
	VAR=""
	VAR=`ls -l $DPATH | grep -ae "README.md"`

	if [ -z "$VAR" ]; then
		echo "-> file does not exist"
		echo "-> create file..."
		cp $SETUP_PATH/README.md $DPATH
	else
		echo "-> file exist"
	fi
	echo -e "Done..."

	echo -e "\n### Checking for config.json"
	VAR=""
	VAR=`ls -l $DPATH | grep -ae "config.json"`

	if [ -z "$VAR" ]; then
		echo "-> file does not exist"
		echo "-> create file..."
		cp $SETUP_PATH/config.json $DPATH
	else
		echo "-> file exist"
	fi
	echo -e "Done..."

	echo -e "\n### Checking for index.js"
	VAR=""
	VAR=`ls -l $DPATH | grep -ae "index.js"`

	if [ -z "$VAR" ]; then
		echo "-> file does not exist"
		echo "-> create file..."
		cp $SETUP_PATH/index.js $DPATH
	else
		echo "-> file exist"
	fi
	echo -e "Done..."

	echo -e "\n### Checking for ethereum activation"
	VAR=""
	VAR=`cat $DPATH/reset.sh | grep -ae "ETHEREUM=" | cut -d "=" -f2`

	if [ "$VAR" == "0" ]; then
		echo "-> ethereum not active"
		echo "-> activate ethereum"
		flock $DPATH/reset.sh sed -i -e "s/ETHEREUM=.*/ETHEREUM=1/" $DPATH/reset.sh
	else
		echo "-> ethereum activated"
	fi
	echo -e "Done..."
}

f_web3() {
	echo -e "\n### Checking for web3"
	VAR=""
	cd $DPATH
	VAR=`npm list --depth=0 | grep -ae "web3"`
	
	if [ -z "$VAR" ]; then
		echo "-> not installed"
		echo "-> install package..."
		npm install web3
	else
		echo "-> package already installed"
	fi
	echo -e "Done..."
}

f_ganache() {
	echo -e "\n### Checking for ganache-cli"
	VAR=""
	cd $DPATH
	VAR=`sudo npm list -g --depth=0 | grep -ae "ganache-cli"`

	if [ -z "$VAR" ]; then
		echo "-> not installed"
		echo "-> install package..."
		sudo npm install -g ganache-cli
	else
		echo "-> package already installed"
	fi
	echo -e "Done..."
}

f_golang() {
	echo -e "\n### Checking for golang"
	VAR=""
	VAR=`sudo dpkg -l | grep -a -e "golang"`

	if [ -z "$VAR" ]; then
		echo "-> not installed"
		echo "-> install package..."
		sudo apt-get -yq install golang
	else
		echo "-> package already installed"
	fi
	echo -e "Done..."
}

f_geth() {
	echo -e "\n### Checking for geth"
	VAR=""
	VAR=`sudo ls -l /usr/local/bin | grep -ae "geth"`
	ARM7=`cat /proc/cpuinfo | grep -ae "ARMv7"`
	ARM6=`cat /proc/cpuinfo | grep -ae "ARMv6"`

	if [ -z "$VAR" ]; then
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
}

f_clear
f_nodejs
f_npm
f_web3
f_ganache
f_files

echo -e "\n"

exit 0