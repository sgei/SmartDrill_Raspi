#!/bin/bash

path="/home/pi/intershop/scripts/drill/"

# auf Standarddisplay ausfuehren
if [ "${DISPLAY::2}" = ":0" ]
then
	/usr/bin/lxterminal --working-directory=$path --command="/bin/bash autostart.sh"
fi