#**peanut - The IoT Squirrel Feeder**


A project to validate the following assumption:

*"The amount of nuts taken by squirrels from a squirrel feeder correlates with upcoming winter weather conditions significantly."*

The IoT Squirrel Feeder's homepage:
http://www.TheSquirrelCafe.com


[Update 2016/09/17]

The directory ESP8266 contains a Arduino IDE Sketch which is used to log environmental weather data. Currently a DHT22 sensor is attached to a NodeMCU v3 board. Sensor readings are published on ThingSpeak. A Watchdog is implemented in case of misbehaviour. A rudimentary UDP packet broadcast with sensor readings has been implemented.

[Update 2016/08/05]

The directory MatLab-Code contains the MinMaxVisu MatLab file which is used to calculate min and max temperature values of the last 24 hours. 


Tweepy - The python twitter lib used:
http://www.tweepy.org

Raspberry Pi Cam Info:
https://www.raspberrypi.org/blog/camera-board-available-for-sale/





