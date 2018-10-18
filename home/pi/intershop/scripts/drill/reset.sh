ls #!/bin/bash

PROG=`basename $0`								# Program-Name
DRILL_PATH=/home/pi/intershop/scripts/drill		# Path for main-script and config-file
DAT_FILE=drill.dat								# Name of the CDAT-file

ETHEREUM=0

LOOP=1

while [ $LOOP -eq 1 ]
do
	RESET=`cat $DRILL_PATH/$DAT_FILE | grep -a -e "RESET" | cut -d "=" -f2`
	TEMP1=$RESET

	cd $DRILL_PATH

	lxterminal --working-directory=$DRILL_PATH --command="python drill.py"

	if [ "$ETHEREUM" == "1" ]; then
		sleep 5
		lxterminal --working-directory=$DRILL_PATH --command="ganache-cli --account=\"0x645a1e7f7d16658f2fb625b25956ed85fe4b3f25e768b99e480249de150e5b8e, 60000000000000000000\" --account=\"0x885d562b23803d62eed698530e18bef8d71b6d9bd535b56bf4a44ff1928fee1e, 0\""

		sleep 15
		lxterminal --working-directory=$DRILL_PATH --command="node $DRILL_PATH/index.js"
		
		sleep 10
	else
		sleep 2
	fi

	while [ $RESET -eq $TEMP1 ]
	do
		sleep 1
		RESET=`cat $DRILL_PATH/$DAT_FILE | grep -a -e "RESET" | cut -d "=" -f2`
		echo $RESET
	done

	# kill drill.py
	kill `ps -aux | grep -a -e "drill.py" | grep -a -v "grep" | tr -s " " | cut -d " " -f2`
	# kill ganace-cli
	if [ "$ETHEREUM" == "1" ]; then
		kill `ps -aux | grep -a -e "ganache-cli" | grep -a -v "grep" | tr -s " " | cut -d " " -f2`
	fi

	sleep 2
done
