#! /usr/bin/python3

import time
import queue
import asyncio
from threading import Thread
# import threading
#import RPi.GPIO as GPIO
import gpiozero

# GPIO.setmode(GPIO.BCM)

BUTTONS = [
  ("left_button", 26),
  ("right_button", 12)
]

# DEBOUNCE=0.1
LONG_PRESS_TIME=2

def Button(q,name,pin):
  gz=gpiozero.Button(pin,hold_time=LONG_PRESS_TIME)
  gz.when_held=lambda:q.put((name,"key_down_long"))
  gz.when_pressed=lambda:q.put((name,"key_down"))
  return gz
  #self.gz.when_released=self.when_released

# class Button(Thread):
#   def __init__(self,q,name,pin):
#     Thread.__init__(self)
#     self.daemon = True
#     self.pin = pin
#     self.name = name
#     self.q = q
#     GPIO.setup(self.pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
#     self.start()
  
#   def run(self):
#     while True:
#       while GPIO.input(self.pin):
#         if GPIO.wait_for_edge(self.pin, GPIO.RISING, timeout=100) != None:
#           break
#       time_down=time.time()
#       self.q.put((self.name,"key_down"))
#       time.sleep(DEBOUNCE)
#       isshort=True
#       while not GPIO.input(self.pin):
#         if GPIO.wait_for_edge(self.pin, GPIO.RISING, timeout=100) != None:
#           break
#         if isshort and time.time()-time_down>LONG_PRESS_TIME:
#           isshort=False
#           self.q.put((self.name,"key_down_long"))
#       self.q.put((self.name,"key_up"))
#       self.q.put((self.name,"short_press" if isshort else "long_press"))
#       time.sleep(DEBOUNCE)

class Buttons():
  def __init__(self, q = queue.Queue()):
    self.q = q
    self.buttons=[Button(self.q,name,pin) for name,pin in BUTTONS]
  
  def get(self):
    r=[]
    while not self.q.empty():
      r.append(self.q.get())
    return r

if __name__=="__main__":
  b=Buttons()
  while True:
    print(b.q.get())
