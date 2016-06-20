#!/usr/bin/env python
import subprocess
import os
import time

import RPi.GPIO as GPIO

BtnPin = 11
Gpin = 12
Rpin = 13

ds18b20 = '28-04162025b3ff'       # Device ID
tweet_enabled = True              # Send tweet on twitter
lid_was_open_before = False       # Only send tweets when lid is closed again
is_eating = False                 # Squirrel status
is_eating_timestamp = time.time() # Set time of grabbing a bite
peanut_count = 0                  # Counter for lid openings
timeout_eating = 60               # Lid openings within x seconds belong to a chowing session


def setup():
  GPIO.setmode(GPIO.BOARD) # Numbers GPIOs by physical location
  GPIO.setup(Gpin, GPIO.OUT) # Set Green Led Pin mode to output
  GPIO.setup(Rpin, GPIO.OUT) # Set Red Led Pin mode to output
  GPIO.setup(BtnPin, GPIO.IN, pull_up_down=GPIO.PUD_UP) # Set BtnPin's mode is input, and pull up to high level(3.3V)
  GPIO.add_event_detect(BtnPin, GPIO.BOTH, callback=detect, bouncetime=200)
	
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
  if tweet_enabled:
    tweet = "twitter set \"%s\"" % tweet_text
    subprocess.call(tweet, shell=True)
    print tweet_text


def send_tweet_eating_finished():
   global peanut_count

   trigger_time = time.strftime("%Y-%m-%d %H:%M:%S")
   temp = read_temp()
   tweet_text = "#IoT - #Squirrel chowed about %d nut(s) down at Parkaue Feeder. %s" % (peanut_count, trigger_time)
   send_a_tweet( tweet_text )
   peanut_count = 0


def send_tweet(x):
  global lid_was_open_before, peanut_count, is_eating, is_eating_timestamp

  # Lid is open
  if x == 0:
    if lid_was_open_before == False:
      lid_was_open_before = True
      peanut_count = peanut_count + 1
      print 'peanut count: %d' % peanut_count
      is_eating_timestamp = time.time()
      if is_eating == False:
        temp = read_temp()
        trigger_time = time.strftime("%Y-%m-%d %H:%M:%S")
        tweet_text = "#IoT - #Squirrel grabbed a nut from Parkaue Feeder right now. \
%s, current temperature: %0.1f C" % (trigger_time, temp) 
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

  print 'Waiting for event...'

  while True:
    if is_eating:
      now_timestamp = time.time()
      time_dif = now_timestamp - is_eating_timestamp
      #print time_dif
      if time_dif > timeout_eating:
        is_eating = False
        #print 'is_eating = False'
        send_tweet_eating_finished()
 
    if time.localtime().tm_sec%2 == 0:
      GPIO.output(Rpin, 0)
      GPIO.output(Gpin, 1)
      #print '0'
    else:
      GPIO.output(Rpin, 1)
      GPIO.output(Gpin, 0)
      #print '1'
    pass


def destroy():
  GPIO.output(Gpin, GPIO.HIGH) # Green led off
  GPIO.output(Rpin, GPIO.HIGH) # Red led off
  GPIO.cleanup() # Release resource


if __name__ == '__main__': # Program start from here
  setup()
  try:
    loop()
  except KeyboardInterrupt: # When 'Ctrl+C' is pressed, the child program destroy() will be executed.
    destroy()
