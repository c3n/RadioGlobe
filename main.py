#!/usr/bin/python3 -u

import display
disp = display.Display()

import re
import os
import json
import time
import queue
import random
import alsaaudio
import threading
import subprocess
from threading import Thread

import rgb_led_proc
import vlc
import encoders
import dial
import button
import geo

PLAY_TIMEOUT_LONG = 10
PLAY_TIMEOUT_SHORT = 2
VOLUME_INCREMENT = 5

class Calib(Thread):
  def __init__(self):
    Thread.__init__(self)
    self.daemon=True
    self.calib=self.load_calib()
    self.last=dict(self.calib)
    self.start()

  def load_calib(self):
    try:
      with open("calib.json") as f:
        return json.load(f)
    except:
      return {"volume":50,"encoder_offsets":[0,0],"paused":True}

  def run(self):
    while True:
      time.sleep(1)
      if self.calib!=self.last:
        calibnow=dict(self.calib)
        time.sleep(5)
        if calibnow==self.calib:
          subprocess.call(["sudo","mount","-o","remount,rw","/"])
          with open("calib.json.new","w") as f:
            f.write(json.dumps(calibnow))
          os.rename("calib.json.new", "calib.json")
          subprocess.call(["sudo","mount","-o","remount,ro","/"])
          self.last=calibnow

def play():
  if station==None or not current_stations:
    print("cant play",station,len(current_stations))
    return
  leds.tuning()
  vlcc.play(current_stations[station]["url"])
  disp.set_station(current_stations[station]["name"],station+1,len(current_stations))

def pause():
  vlcc.stop()
  leds.paused()
  disp.pause()

def set_volume():
  mixer.setvolume(calib.calib["volume"])
  disp.set_volume(calib.calib["volume"])

def change_station(param):
  global station
  if not current_stations:
    return
  leds.jogged(param)
  station=(station+param)%len(current_stations)
  leds.jogged(param)
  play()

def on_left_jog(param):
  change_station(param)

def on_left_button(param):
  if param=="key_down":
    calib.calib["paused"]=not calib.calib["paused"]
    if calib.calib["paused"]:
      pause()
    else:
      play()

def on_right_jog(param):
  calib.calib["volume"]=min(100,max(0,calib.calib["volume"]+param*VOLUME_INCREMENT))
  set_volume()
  leds.volume(calib.calib["volume"])

def on_right_button(param):
  if param=="key_down_long":
    leds.calibrate()
    calib.calib["encoder_offsets"]=encoders.zero()
    disp.message("Calibrated")

def on_lat_lon_moved(param):
  global station
  if station!=None:
    leds.tuning()
    vlcc.stop()
    station=None
  dist_km,city,current_stations=stations.query(*param)
  disp.set_location(*param)
  disp.set_city(city)
  disp.set_station(f"{dist_km}km away")

def on_lat_lon_stuck(param):
  global current_stations,first,station
  dist_km,city,current_stations=stations.query(*param)
  disp.set_location(*param)
  if dist_km>1000:
    disp.set_city(f"{city}: {dist_km}km")
    disp.set_station("Too far away", 0, 0)
  elif not current_stations:
    disp.set_city(city)
    disp.set_station("No Stations here", 0, 0)
  else:
    station=random.randint(0,len(current_stations)-1)
    disp.set_city(city)
    if first:
      first=False
      if calib.calib["paused"]:
        print("start paused")
        pause()
      else:
        print("start playing")
        play()
    else:
      calib.calib["paused"]=False
      play()

def on_vlc(param):
  if param=="playing":
    leds.playing()
  else:
    if vlcc.play_start_at!=None:
      trying_for=time.time()-vlcc.play_start_at
      if param=="trying":
        if trying_for>PLAY_TIMEOUT_LONG:
          change_station(1)
      elif param=="stopped":
        if trying_for>PLAY_TIMEOUT_SHORT:
          change_station(1)

def handle_event(evt,param):
  globals()[f"on_{evt}"](param)

def loop():
  disp.message("Started",1)
  while True:
    try:
      evt=in_q.get(timeout=0.2)
    except queue.Empty:
      continue
    handle_event(*evt)

if __name__=="__main__":
  first = True
  station = None
  current_stations = None
  leds = rgb_led_proc.RGBLeds()
  in_q = queue.Queue()
  calib=Calib()
  mixer=alsaaudio.Mixer()
  dials = dial.Dials(in_q)
  buttons = button.Buttons(in_q)
  encoders = encoders.Encoders(in_q,calib.calib["encoder_offsets"])
  vlcc=vlc.VLC(in_q)
  stations=geo.Stations()
  set_volume()
  leds.tuning()
  loop()
