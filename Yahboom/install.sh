#!/bin/sh

sudo cp ./yahboom.service /etc/systemd/system/yahboom.service

# reload the systemctl utility
systemctl daemon-reload

# start our daemon
systemctl start yahboom.service

# enable the deamon
sudo systemctl enable yahboom

echo 'install ok!'
