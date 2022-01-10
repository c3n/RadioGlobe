#!/usr/bin/python3

import sys
import math
import time
from threading import Thread
from rpi_ws281x import PixelStrip, Color

# LED strip configuration:
LED_COUNT = 8         # Number of LED pixels.
LED_PIN = 13          # GPIO pin connected to the pixels (18 uses PWM!).
# LED_PIN = 10        # GPIO pin connected to the pixels (10 uses SPI /dev/spidev0.0).
LED_FREQ_HZ = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA = 10          # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 255  # Set to 0 for darkest and 255 for brightest
LED_INVERT = False    # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL = 1       # set to '1' for GPIOs 13, 19, 41, 45 or 53

COLORS={ #der vierte ist die animationsgeschwindigkeit
  "off":[0,0,0],
  "starting":[30,0,30,5],
  "calibrate":[0,255,0],
  "volume":[255,100,100],
  "jogged":[60,60,255],
  "tuning":[255,255,0,20],
  "playing":[255,255,255,10],
  "paused":[30,0,0,1]
}

for v in COLORS.values():
  v[:3]=[x//4 for x in v[:3]]

JOG_LIT=3

class RGBLeds(Thread):
  def __init__(self):
    Thread.__init__(self)
    self.daemon = True
    self.strip = PixelStrip(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
    self.strip.begin()
    self.state="starting"
    self.jog=None
    self.vol=None
    self.calibrated=None
    self.start()

  def run(self):
    while True:
      while self.vol!=None:
        nowvol=self.vol
        self.vol=None
        midled=int(nowvol*LED_COUNT/100)
        for i in range(LED_COUNT):
          j=LED_COUNT-1-i
          if i<midled:
            self.strip.setPixelColorRGB(j,*COLORS["volume"])
          elif i>midled:
            self.strip.setPixelColorRGB(j,*COLORS["off"])
          else:
            f=(nowvol/100-midled/LED_COUNT)*LED_COUNT
            self.strip.setPixelColorRGB(j,*[int(x*f) for x in COLORS["volume"]])
        self.strip.show()
        for i in range(30):
          if self.vol!=None:
            break
          time.sleep(0.1)
      if self.jog!=None:
        for j in range(LED_COUNT+JOG_LIT-1) if self.jog<0 else range(LED_COUNT+JOG_LIT-2,-1,-1):
          for i in range(LED_COUNT):
            self.strip.setPixelColorRGB(i,*COLORS["jogged" if j-JOG_LIT<i<=j else "off"])
          self.strip.show()             
          time.sleep(0.05)
        self.jog=None
      elif self.calibrated:
        for i in range(3):
          for i in range(LED_COUNT):
            self.strip.setPixelColorRGB(i,*COLORS["calibrate"])
          self.strip.show()
          time.sleep(0.2)
          for i in range(LED_COUNT):
            self.strip.setPixelColorRGB(i,*COLORS["off"])
          self.strip.show()
          time.sleep(0.5)
        self.calibrated=None
      else:
        col=COLORS[self.state]
        if len(col)>3:
          n=time.time()*col[3]
          for i in range(LED_COUNT):
            self.strip.setPixelColorRGB(i,*[int(x*(math.sin(n+i*6/LED_COUNT)/3+0.66)) for x in col[:3]])
        else:
          for i in range(LED_COUNT):
              self.strip.setPixelColorRGB(i,*col)
        self.strip.show()
        time.sleep(0.05)
  
  def volume(self,volume):
    self.vol=volume

  def jogged(self,direction):
    self.jog=direction

  def calibrate(self):
    self.calibrated=True

  def tuning(self):
    self.state="tuning"

  def playing(self):
    self.state="playing"

  def paused(self):
    self.state="paused"

if __name__=="__main__":
  leds=RGBLeds()
  for line in sys.stdin:
    x=line.strip().split()
    if len(x)==1:
      getattr(leds, x[0])()
    elif len(x)==2:
      getattr(leds, x[0])(int(x[1]))
    else:
      print("error in arguments:",x)