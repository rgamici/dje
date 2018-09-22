#!/bin/sh
eval "export $(egrep -z DBUS_SESSION_BUS_ADDRESS /proc/$(pgrep -u $LOGNAME openbox)/environ)";

#Code:
DISPLAY=:0 notify-send 'DJE' 'Dje disponível' -i starred
