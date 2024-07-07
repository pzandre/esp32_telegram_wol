#!/bin/bash

pkill screen

for file in boot.py main.py;
do
    echo "refreshing $file"
    if [ -z "$1" ];
    then
        ampy --port /dev/ttyACM0 rm $file
    fi
    ampy --port /dev/ttyACM0 put $file
done