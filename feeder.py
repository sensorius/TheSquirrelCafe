#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import time
import RPi.GPIO as GPIO
import tweepy
import subprocess
import urllib2 

from twitter_token import *  # File containing twitter app keys and tokens

BtnPin = 11
Gpin   = 12
Rpin   = 13

ds18b20 = '28-04162025b3ff'       # Device ID
tweet_enabled = True              # Send tweet on twitter
lid_was_open_before = False       # Only send tweets when lid is closed again
is_eating = False                 # Squirrel eating status
is_eating_timestamp = time.time() # Set time of grabbing a bite
starts_eating_timestamp = time.time() # First nut grabbed
peanut_count = 0                  # Counter for lid openings
timeout_eating = 90               # Lid openings within x seconds belong to a chowing session
api = None
image_file = None                 # File with feeder image captured
video_file = None                 # File with feeder video captured
video_saved = False

def setup():
  global api
  GPIO.setmode(GPIO.BOARD) # Numbers GPIOs by physical location
  GPIO.setup(Gpin, GPIO.OUT) # Set Green Led Pin mode to output
  GPIO.setup(Rpin, GPIO.OUT) # Set Red Led Pin mode to output
  GPIO.setup(BtnPin, GPIO.IN, pull_up_down=GPIO.PUD_UP) # Set BtnPin's mode is input, and pull up to high level(3.3V)
  GPIO.add_event_detect(BtnPin, GPIO.BOTH, callback=detect, bouncetime=200)
  auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
  auth.secure = True
  auth.set_access_token(access_token, access_token_secret)

  api = tweepy.API(auth)

  # If the authentication was successful, you should
  # see the name of the account print out
  print(api.me().name)	
  print 'Setup finished'


def read_temp():
  location = '/sys/bus/w1/devices/' + ds18b20 + '/w1_slave'
  tfile = open(location)
  text = tfile.read()
  tfile.close()
  secondline = text.split("\n")[1]
  temperaturedata = secondline.split(" ")[9]
  temperature = float(temperaturedata[2:])
  temperature = temperature / 1000
  return temperature

def set_led(x):
  if x == 0:
    GPIO.output(Rpin, 1)
    GPIO.output(Gpin, 0)
  if x == 1:
    GPIO.output(Rpin, 0)
    GPIO.output(Gpin, 1)


def send_a_tweet(tweet_text):
  global api
  if tweet_enabled:
    tweet_text = tweet_text + ' - RaspberryPi powered.'
    api.update_status(status=tweet_text)
    #subprocess.call(tweet, shell=True)
  print tweet_text

def send_a_tweet_with_image(tweet_text):
  global api, image_file
  if tweet_enabled:
    tweet_text = tweet_text + ' - RaspberryPi powered.'
    api.update_with_media(image_file, status=tweet_text)

  print tweet_text    

def update_thingspeak( payload ):

  baseurl = "https://api.thingspeak.com/update?api_key=%s" % thingspeak_api_key
  f = urllib2.urlopen(baseurl + payload)
  print f.read()
  f.close()
  
    
def save_a_image():
  global image_file

  image_file = "img_feeder.%s.jpg" % time.strftime("%Y-%m-%d-%H-%M-%S")
  cmd = "raspistill -o %s -t 200 -w 640 -h 480 --hflip --vflip" % image_file
  subprocess.Popen(cmd, shell=True)


def save_a_video():
  global video_file

  video_file = "vid_feeder.%s.mp4" % time.strftime("%Y-%m-%d-%H-%M-%S")
  cmd = "raspivid -o %s -w 640 -h 360  -hf -vf " % video_file
  subprocess.Popen(cmd, shell=True)


def send_tweet_eating_finished():
   global peanut_count

   trigger_time = time.strftime("%H:%M:%S UTC+2")
   
   # More than one nut?
   if peanut_count == 1:
   	nut__text = "nut"
   else:
   	nut_text = "nuts"
   
   diff_time = is_eating_timestamp - starts_eating_timestamp	
   if diff_time > 0 and peanut_count > 1:
   	npm = (peanut_count-1) / diff_time * 60
   	tweet_text = "#Squirrel chowed %d %s down at #IoT Feeder. v=%.2f[npm] %s" % (peanut_count, nut_text, npm, trigger_time)
        send_a_tweet_with_image( tweet_text )
        update_thingspeak("&field1=%d&field2=%.1f&field3=%.2f" % (peanut_count, read_temp(), npm))

   peanut_count = 0


def send_tweet(x):
  global lid_was_open_before, peanut_count, is_eating, is_eating_timestamp, starts_eating_timestamp
  global video_saved

  # Lid is open
  if x == 0:
    if lid_was_open_before == False:
      lid_was_open_before = True
      if time.time() - is_eating_timestamp > 5: # 5 secs minimum for eating a nut
      	peanut_count = peanut_count + 1
      print 'peanut count: %d' % peanut_count
      is_eating_timestamp = time.time()
      if peanut_count == 3 and video_saved == False:
        save_a_video()
        video_saved = True
      if is_eating == False:
        video_saved = False
        temp = read_temp()
        starts_eating_timestamp = is_eating_timestamp
        
        trigger_time = time.strftime("%Y-%m-%d %H:%M:%S")
        tweet_text = "#Squirrel grabbing a nut from #IoT Feeder right now. %s, t=%0.1f[C]" % (trigger_time, temp) 
        save_a_image()
        send_a_tweet( tweet_text )
        is_eating = True

  # Lid is closed
  if x == 1:
    lid_was_open_before = False


def detect(chn): 
  set_led(GPIO.input(BtnPin))
  send_tweet(GPIO.input(BtnPin))


def loop():
  global is_eating_timestamp, is_eating

  thingspeak_temp_posted = False

  print 'Waiting for event...'

  while True:
    time.sleep(0.01) # Avoid CPU overloading
    if is_eating:
      # Check if lid had been closed for at least e.g. 60 secs
      if (time.time()-is_eating_timestamp) > timeout_eating:
        is_eating = False
        send_tweet_eating_finished()
    # Blinking LED to indicate that script is running
    if time.localtime().tm_sec%2 == 0:
      GPIO.output(Rpin, 0)
      GPIO.output(Gpin, 1)
      # print '\rX0',
    else:
      GPIO.output(Rpin, 1)
      GPIO.output(Gpin, 0)
      # print '\r0X',

    if time.localtime().tm_min%5 == 0:
      if thingspeak_temp_posted == False:
	update_thingspeak( '&field2=%.1f' % read_temp() )
        thingspeak_temp_posted = True
    else:
      thingspeak_temp_posted = False

    pass




def destroy():
  GPIO.output(Gpin, GPIO.HIGH) # Green LED off
  GPIO.output(Rpin, GPIO.HIGH) # Red LED off
  GPIO.cleanup() # Release resource


if __name__ == '__main__': # Program start from here
  setup()
  try:
    loop()
  except KeyboardInterrupt: # When 'Ctrl+C' is pressed, the child program destroy() will be executed.
    destroy()
