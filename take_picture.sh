#!/bin/bash

DATE=$(date +"%Y-%m-%d_%H-%M")

raspistill -o /home/pi/bilder/foto_$DATE.jpg
#EMAIL=reslmcmmusic@gmx.at
#cd /home/pi/bilder
#echo "Bild aus der Garage. lg Überwachungsanlage" | mailx -s "Bild aus der Garage" -a foto_$DATE.jpg reslmcmmusic@gmx.at
mpack -s "Bild aus der Garage" -a /home/pi/bilder/foto_$DATE.jpg reslmcmmusic@gmx.at
echo "From the send script: Done"
cd
