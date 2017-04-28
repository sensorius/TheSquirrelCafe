***The Squirrel Cafe - An Internet Connected Feeder***


A project to validate the following assumption:

*"The amount of nuts taken by squirrels from a squirrel feeder correlates with upcoming winter weather conditions significantly."*

The IoT Squirrel Feeder's homepage:
http://www.TheSquirrelCafe.com


**Feeder Wiring:** 
![Wiring Sketch](https://github.com/sensorius/peanut/blob/master/docs/feeder-wiring-reed-tm1637.jpg "Wiring of Reed Switch an LED Display")

**Useful shell commands**

A 'live' view of a logfile:
<code>tail -f /logs/feeder.log</code>

Start a vncserver:
<code>vncserver :1</code>

Start feeder.py in the background:
<code>python feeder.py &</code>

List 'feeder' processes running on the system:
<code>ps aux | grep feeder</code>

Kill process by PID:
<code>kill PID</code> or <code>kill KILL PID</code> 



**Useful Weblinks**

* Tweepy - The python twitter lib used: http://www.tweepy.org

* Raspberry Pi Cam Info: https://www.raspberrypi.org/blog/camera-board-available-for-sale/

* Launch Python script on startup: http://www.instructables.com/id/Raspberry-Pi-Launch-Python-script-on-startup/

* Using a standard USB Webcam: https://www.raspberrypi.org/documentation/usage/webcams/

* Driver library for TM1637 7 Segment LED Display: https://github.com/timwaizenegger/raspberrypi-examples/tree/master/actor-led-7segment-4numbers


