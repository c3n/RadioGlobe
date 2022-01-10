#! /usr/bin/python3
import time
import threading
import liquidcrystal_i2c
from unidecode import unidecode

DISPLAY_I2C_ADDRESS = 0x27
DISPLAY_I2C_PORT = 1
DISPLAY_COLUMNS = 20
DISPLAY_ROWS = 4

class Display (threading.Thread):
  def __init__(self):
    threading.Thread.__init__(self)
    self.daemon=True
    self.lcd = liquidcrystal_i2c.LiquidCrystal_I2C(DISPLAY_I2C_ADDRESS, DISPLAY_I2C_PORT, numlines=DISPLAY_ROWS)
    self.set_city("Starting...")
    self.set_location(0,0)
    self.set_volume(0)
    self.set_station("?",0,0)
    self.message("RadioGlobe Starting",120)
    self.start()

  def printcenter(self,line,s):
    self.lcd.printline(line,s[:DISPLAY_COLUMNS].center(DISPLAY_COLUMNS))
  
  def printsplit(self,line,l,r):
    blanks=max(1,DISPLAY_COLUMNS-len(l)-len(r))
    txt=l+" "*blanks+r
    self.lcd.printline(line,txt[:DISPLAY_COLUMNS])

  def run(self):
    while True:
      if self.msg!=None:
        self.printcenter(0,"")
        self.printcenter(1,self.msg)
        self.printcenter(2,"")
        self.printcenter(3,"")
        self.msg=None
      if self.msg_end_time!=None and time.time()>self.msg_end_time:
        self.msg_end_time=None
      if self.msg_end_time!=None:
        continue
      if self.location_changed:
        self.location_changed = False
        self.printcenter(0,f"{abs(self.lat):.1f}{'S'if self.lat<0 else 'N'} {abs(self.lon):.1f}{'W'if self.lon<0 else 'E'}")
      if self.city_changed:
        self.city_changed = False
        self.printcenter(1,self.city)
        #self.printcenter(1,f"{self.city}: {self.station_num}/{self.station_count}" if self.station_count else self.city)
      if self.station_changed:
        self.station_changed = False
        self.printcenter(2,self.station_name)
      if self.last_row_changed:
        self.last_row_changed = False
        if self.paused:
          self.printsplit(3,"Pause",f"{self.volume}%")
        else:
          self.printsplit(3,f"{self.station_num}/{self.station_count}",f"{self.volume}%")
      time.sleep(0.1)

  def message(self, msg, duration=3):
    self.msg=msg
    self.msg_end_time=time.time()+duration
    self.location_changed=True
    self.city_changed=True
    self.station_changed=True
    self.last_row_changed=True
    print("message",msg)

  def set_city(self,city):
    self.city=unidecode(city)
    self.city_changed=True
    print("city",city)
  
  def set_location(self,lat,lon):
    self.lat=lat
    self.lon=lon
    self.location_changed=True
    print("location",lat,lon)
  
  def set_volume(self, volume):
    self.volume=volume
    self.last_row_changed=True
    print("volume",volume)
  
  def set_station(self,name,n=0,count=0):
    self.station_name=unidecode(name)
    self.station_num=n
    self.station_count=count
    self.paused=False
    self.station_changed=True
    self.last_row_changed=True
    print("station",name,n,count)
  
  def pause(self):
    self.paused=True
    self.last_row_changed=True
