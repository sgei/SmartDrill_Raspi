#!/bin/bash

PROG=`basename $0`							# Program-Name
#TEMP0=/tmp/$PROG.$$-0						# TMP-File

path="/home/pi/intershop/scripts/drill/"
azure_file="smartdrill_azure.py"
output_file="/tmp/drill.val"
reset_file="reset.sh"

#trap '\rm -f $TEMP0; exit 1' 1 2 3 9 15

#> $TEMP0

# auf Standarddisplay ausfuehren
if [ "${DISPLAY::2}" = ":0" ]
then

	# call RESET web service to reset showcase
	#curl http://deviceservicea.azurewebsites.net/devices/473095323502/reset

	sleep 5

	# create Output-File
	touch $output_file

	# start AZURE-Upload-Script
	lxterminal --working-directory=$path --command="python $azure_file" &

	sleep 10

	lxterminal --working-directory=$path --command="/bin/bash $reset_file" &

fi

#rm -rf $TEMP0
