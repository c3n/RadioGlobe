#! /usr/bin/python3
import time
import queue
import gpiozero
#import RPi.GPIO as GPIO
from threading import Thread

DIALS = [
  ("right_jog", 16, 25), 
  ("left_jog", 24, 23)
]

def Dial(q,name,p1,p2):
  gz=gpiozero.RotaryEncoder(p1,p2)
  gz.when_rotated_clockwise=lambda:q.put((name,1))
  gz.when_rotated_counter_clockwise=lambda:q.put((name,-1))
  return gz

# class Dial(Thread):
#   def __init__(self, q, name, pin1, pin2):
#     Thread.__init__(self)
#     self.daemon = True
#     self.q = q
#     self.name = name
#     self.pin1 = pin1
#     self.pin2 = pin2
#     GPIO.setmode(GPIO.BCM)
#     GPIO.setup([self.pin1, self.pin2], direction=GPIO.IN, pull_up_down=GPIO.PUD_UP)
#     self.start()

#   def run(self):
#     while True:
#       GPIO.wait_for_edge(self.pin1, GPIO.FALLING)
#       v=GPIO.input(self.pin2)
#       self.q.put((self.name,v*2-1))
#       GPIO.wait_for_edge(self.pin2, GPIO.BOTH)
#       GPIO.wait_for_edge(self.pin1, GPIO.RISING)

class Dials():
  def __init__(self, q = queue.Queue()):
    self.q = q
    self.dials = [Dial(self.q,name,pin1,pin2) for name,pin1,pin2 in DIALS]
  
if __name__=="__main__":
  d=Dials()
  while True:
    print(d.q.get())
