#!/bin/bash

path="/home/pi/intershop/scripts/drill/"

# nicht auf Standarddisplay ausfuehren, nur in VNC-Session
if [ "${DISPLAY::2}" = ":1" ]
then
	/usr/bin/lxterminal --working-directory=$path --command="/bin/bash autostart.sh"
fi