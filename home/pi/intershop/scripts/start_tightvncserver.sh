#!/bin/bash

PID=`ps -C Xtightvnc -o pid= | sed 's/^ //'`

case "$1" in
start)
	if [ -z "$PID" ]
	then
		# starte tightvncserver im Hintergrund und leite die Ausgaben um
		nohup vncserver -name ViSpro -geometry 1670x970 -depth 16 :1 >/dev/null 2>&1 &
		#nohup vncserver -name ViSpro -geometry 1340x640 -depth 16 :1 >/dev/null 2>&1 &
		#PID="$!"
		PID=`ps -C Xtightvnc -o pid= | sed 's/^ //'`
		echo "tightvncserver gestartet..."
	else
		echo "tightvncserver laeuft schon (PID: $PID)..."
	fi
;;
stop)
	if [ ! -z "$PID" ]
	then
		# stoppt tightvncserver
		vncserver -kill :1
		echo "tightvncserver gekillt (PID: $PID)..."
	else
		echo "tightvncserver nicht gestartet..."
	fi
;;
*)
	echo "Usage: $0 {start|stop}"
	exit 1
esac

exit 0
