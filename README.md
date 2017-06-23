***The Squirrel Cafe - An Internet Connected Feeder***


A project to validate the following assumption:

*"The amount of nuts taken by squirrels from a squirrel feeder correlates with upcoming winter weather conditions significantly."*

The IoT Squirrel Feeder's homepage:
http://www.TheSquirrelCafe.com


**Feeder Wiring:** 

<img src="/docs/feeder-wiring-reed-tm1637.jpg" width="480">

**Prerequisites**

Currently, I'm using a Logitech C270 USB webcam to capture photos of the squirrels at the nut feeder. Therefore you need to install a USB Webcam package. I've opted for the 'fswebcam' package.

<code>sudo apt-get install fswebcam</code>

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

* USB Webcam Guide: http://elinux.org/RPi_USB_Webcams

* Launch Python script on startup: http://www.instructables.com/id/Raspberry-Pi-Launch-Python-script-on-startup/

<code>
@reboot sudo sh /home/pi/peanut/launcher.sh >/home/pi/peanut/logs/cronlog.log 2>&1
</code>

* Using a standard USB Webcam: https://www.raspberrypi.org/documentation/usage/webcams/

* Driver library for TM1637 7 Segment LED Display: https://github.com/timwaizenegger/raspberrypi-examples/tree/master/actor-led-7segment-4numbers

* Restart launcher.sh script if exception kicks in using crontab: https://unix.stackexchange.com/questions/107939/how-to-restart-the-python-script-automatically-if-it-is-killed-or-dies

<code>
*/5 * * * * pgrep -f feeder.py | pgrep python | pgrp sudo || sudo sh /home/pi/peanut/launcher.sh >/home/pi/peanut/logs/cronlog.log 2>&1
</code>



