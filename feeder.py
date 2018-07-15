#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

import os
import time
import RPi.GPIO as GPIO
import tweepy
import subprocess
import urllib2 
import sys
import time
import tm1637
import random 

from twitter_token import *           # File containing twitter app keys and tokens

BtnPin = 17                           # Lid open sensor

tweeting_enabled = True               # Send tweet on twitter
tweet_image = True
squirrel_is_present = False           # Squirrel presence status
lid_open_timestamp = time.time()      # Set time of grabbing a bite
starts_eating_timestamp = time.time() # First nut grabbed, first opening of lid
peanut_count = 0                      # Counter for lid openings
peanut_count_old = 0
timeout_presence = 180                # Lid openings within x seconds belong to a chowing session, adjust for food type!
Tweepy = None
image_file = 'None'                   # File with feeder image captured
image_file_saved_flag = False         # File saved flag
video_file = None                     # File with feeder video captured


Display = tm1637.TM1637(23,24,tm1637.BRIGHT_TYPICAL)

LOGFILE='logs/feeder.log'
DATAFILE='logs/data.csv'

def writelog(message):
  with open(LOGFILE,'a') as f:
    f.write("{0} {1}\n".format(time.asctime( time.localtime(time.time())),
                                   message))

def writedata(time, nuts, duration):
  with open(DATAFILE,'a') as f:
    f.write("{0},{1},{2}\n".format(date, time, nuts, duration))

def destroy():
  writelog('Destroy')
  Display.Clear()
  GPIO.cleanup() # Release resource

def setup():
  global Tweepy

  GPIO.setmode(GPIO.BCM) # Numbers GPIOs 
  GPIO.setup(BtnPin, GPIO.IN, pull_up_down=GPIO.PUD_UP) # Set BtnPin's mode is input, and pull up to high level(3.3V)
  # GPIO.add_event_detect(BtnPin, GPIO.RISING, callback=lid_open, bouncetime=200)
  GPIO.add_event_detect(BtnPin, GPIO.FALLING, callback=lid_open, bouncetime=400)

  Display.Clear()
  Display.SetBrightnes(5)

  auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
  auth.secure = True
  auth.set_access_token(access_token, access_token_secret)

  Tweepy = tweepy.API(auth)

  # If the authentication was successful, you should
  # see the name of the account print out
  # Doesn't work at startup using crontab...?
  #writelog(Tweepy.me().name)	
  writelog('Setup finished.')
 
  if os.path.isfile('images/img_feeder.2017-08-10-16-21-34.jpg') is False:
    writelog('...not present')
  else:
    writelog('...is present')


def send_a_tweet_with_image(tweet_text):
  tweet_text = tweet_text + ' An #IoT project to predict how cold it\'ll be next winter. #ThingSpeak'
  if tweeting_enabled:
    writelog('send_a_tweet_with_image')
    writelog(image_file)
    writelog(tweet_text)
    try:
      writelog('Before update with media')
      # check if file exists
      Tweepy.update_with_media(image_file, status=tweet_text)
      writelog('After update with media')
    except Tweepy.TweepError as err:
      writelog('Exception on sending a tweet')
      writelog(err)
      destroy()
  writelog('Tweet sent')    


def send_a_tweet_with_video(tweet_text):
  tweet_text = tweet_text + ' - RaspberryPi powered.'
  if tweeting_enabled:
    media = Tweepy.upload_chunked(video_file)
    Tweepy.update_status(status=tweet_text, media_ids=[media.media_id])
  writelog(tweet_text)


def update_thingspeak( payload ):
  baseurl = "https://api.thingspeak.com/update?api_key=%s" % thingspeak_api_key
  f = urllib2.urlopen(baseurl + payload)
  writelog(f.read())
  f.close()
  
    
def save_a_image():
  global image_file

  writelog('Capture and save image')
  image_file = "images/img_feeder.%s.jpg" % time.strftime("%Y-%m-%d-%H-%M-%S")
  #cmd = "sudo raspistill -o %s -t 200 -w 640 -h 480 --hflip --vflip" % image_file
  cmd = "sudo fswebcam -c fswebcam.cfg %s" % image_file
  wait_in_secs = random.randint(0,2)*0.25
  time.sleep(wait_in_secs)
  writelog(image_file)
  subprocess.Popen(cmd, shell=True)
  #args = shlex.split(cmd)
  #subprocess.call(args)
  #time.sleep(4)

  

def save_a_video():
  global video_file

  writelog('Capture and save video')
  video_file = "videos/vid_feeder.%s.h264" % time.strftime("%Y-%m-%d-%H-%M-%S")
  cmd = "raspivid -o %s -w 640 -h 360 -t 20000 -hf -vf " % video_file
  subprocess.Popen(cmd, shell=True)


def squirrel_seems_to_have_had_enough():
  global peanut_count, peanut_count_old, image_file_saved_flag, image_file

  trigger_time = time.strftime("%H:%M:%S %Z")
  writelog('Squirrel seems to have had enough') 
  # More than one nut?
  if peanut_count == 2:
    nut_text = "nut"
  else:
    nut_text = "nuts"
  
  # Time difference of last and first lid opening 
  diff_time = lid_open_timestamp - starts_eating_timestamp	
  writelog('Before if diff_time')
  if diff_time > 0 and peanut_count > 1:
    npm = (peanut_count-0) * 0.5 / diff_time * 60.0
    diff_text = ("%.2f min" % (diff_time / 60.0))
    npm_text = "v=%.2f[npm]" % npm
    tweet_text = "#Squirrel chowed down on %.1f %s for %s at %s." % (peanut_count*0.5, nut_text, diff_text, trigger_time)
    writelog('Within diff')
    writelog(tweet_text)
    writelog(npm)
    # trigger_date = time.strftime("%Y-%M-%D", lid_open_timestamp)
    # print(trigger_date)
    # writedata(date = trigger_date, time = trigger_time, nuts = peanut_count*0.5, duration = diff_time)
    send_a_tweet_with_image( tweet_text )
    image_file = 'None'
    update_thingspeak("&field1=%d&field2=%.1f&field3=%.2f" % (peanut_count*0.5, 0, npm))

  peanut_count_old = peanut_count
  peanut_count = 0
  image_file_saved_flag = False
   


def lid_open(chn):
  global image_file, image_file_saved_flag, lid_open_timestamp, starts_eating_timestamp, squirrel_is_present, peanut_count 
  
  writelog('Lid has been opened')


  squirrel_is_present = True
  # To eat a nut, you need at least 5 seconds
  if time.time() - lid_open_timestamp > 5:
    writelog('Increment nut count')
    peanut_count += 1
    Display.Show([0x7f,0x7f,peanut_count/10,peanut_count%10])
    writelog(peanut_count)

    if os.path.isfile(image_file) is False:
      image_file_saved_flag = False
      writelog('Image file not found')
    else:
      image_file_saved_flag = True
      writelog('Image file exists')

  lid_open_timestamp = time.time() 
  
  if peanut_count == 1:
    starts_eating_timestamp = time.time()

  if image_file_saved_flag is False:
    save_a_image()
    #save_a_video()

  writelog('end lid_open')
  


def loop():
  global squirrel_is_present

  writelog('Waiting...')
  flag_writelog = True
  while True:
    time.sleep(0.2) # Avoid CPU overloading

    if squirrel_is_present:
      # Check if lid hasn't been opened for at least e.g. 90 secs
      # If so, assume squirrel has left the spot
      if (time.time()-lid_open_timestamp) > timeout_presence:
        squirrel_is_present = False
	squirrel_seems_to_have_had_enough()
    else:
      try: 
        if time.time()%2 > 1.0:
          Display.Show([peanut_count_old/10,peanut_count_old%10,0x7f,0x7f])
          Display.ShowDoublepoint(0)
        else:
          Display.Show([0x7f,0x7f,0x7f,0x7f])
          Display.ShowDoublepoint(1)
      except:
        writelog('Ooops, display exception.')
      # Write a alive message to logfile every 12 hours 
      if not int(time.time())%(12*3600): 
        if flag_writelog:
          writelog('Waiting for a squirrel to appear.')
        flag_writelog = False
      else:
        flag_writelog = True



if __name__ == '__main__': # Program start from here
  setup()
  try:
    loop()
  except KeyboardInterrupt: # When 'Ctrl+C' is pressed, the child program destroy() will be executed.
    destroy()
