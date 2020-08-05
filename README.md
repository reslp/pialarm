# Raspberry PI based surveillance camera

## A crontab jobs needs to be added witn crontab -e 

```
@reboot sh /home/pi/alarm_launcher.sh > /home/pi/logs/alarm_log.txt 2>&1
```

