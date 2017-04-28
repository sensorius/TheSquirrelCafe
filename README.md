#**peanut - The Squirrel Cafe**


A project to validate the following assumption:

*"The amount of nuts taken by squirrels from a squirrel feeder correlates with upcoming winter weather conditions significantly."*

The IoT Squirrel Feeder's homepage:
http://www.TheSquirrelCafe.com


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


**USB Webcam**

You can use a standard USB Webcam to take pictures an a Raspberry Pi using fswebcam. Install the fswebcam package:
<code>sudo apt-get install fswebcam</code>
To take a picture: <code>fswebcam image.jpg</code> 


**Useful Weblinks**

Tweepy - The python twitter lib used:
http://www.tweepy.org

Raspberry Pi Cam Info:
https://www.raspberrypi.org/blog/camera-board-available-for-sale/





