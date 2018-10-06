#!/bin/bash

clear

#echo -e "\n### Deleting /var/lib/dhcp/dhclient.eth0.leases..."
#sudo rm -f /var/lib/dhcp/dhclient.eth0.leases

echo -e "\n### apt-get autoremove ..."
sudo apt-get autoremove

echo -e "\n### apt-get autoclean ..."
sudo apt-get autoclean

echo -e "\n### apt-get clean ..."
sudo apt-get clean

echo -e "\n### sync ..."
sudo sync

echo -e "\n"

exit 0
